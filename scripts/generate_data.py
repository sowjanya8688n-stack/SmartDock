from __future__ import annotations
import argparse, csv, hashlib, json, random, sqlite3
from collections import Counter, defaultdict
from datetime import date, datetime, time, timedelta
from pathlib import Path

SEED = 20261022
START = date(2026, 1, 1)
FACILITIES, DOCKS, APPOINTMENTS, DAYS = 10, 100, 20_000, 60
ROOT = Path(__file__).resolve().parents[1] / 'backend' / 'generated_data'

FIELDS = {
'facilities': ['facility_id','name','city','timezone','effective_from','status'],
'docks': ['dock_id','facility_id','dock_type','hazmat_certified','reefer_power','active'],
'yard_slots': ['yard_slot_id','facility_id','slot_type','capacity','active'],
'carriers': ['carrier_id','name','active'],
'vehicles': ['vehicle_id','carrier_id','vehicle_type','capacity_pallets','reefer_capable','hazmat_certified','active'],
'shipments': ['shipment_id','facility_id','carrier_id','vehicle_id','direction','pallets','temperature_controlled','hazardous','handling_requirement_id','requested_date'],
'handling_requirements': ['handling_requirement_id','shipment_id','required_dock_type','min_service_minutes','max_service_minutes','requires_reefer','requires_hazmat'],
'labor_shifts': ['labor_shift_id','facility_id','shift_date','start_time','end_time','team_count','active'],
'appointments': ['appointment_id','shipment_id','facility_id','carrier_id','vehicle_id','dock_id','yard_slot_id','appointment_date','window_start','window_end','service_minutes','status','scheduled_at'],
'checkin_events': ['checkin_id','appointment_id','event_time','event_type','minutes_early_late'],
'exceptions': ['exception_id','appointment_id','issue_type','cause_code','severity','detected_at','resolution_status'],
'events': ['event_id','appointment_id','event_type','event_time','source','details'],
'ground_truth': ['label_id','appointment_id','issue_type','expected_decision','rule'],
}

def iso(d): return d.isoformat()
def dt(d, hm): return datetime.combine(d, time.fromisoformat(hm))
def dump_csv(folder, name, rows):
    path=folder/f'{name}.csv'
    with path.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=FIELDS[name]); w.writeheader(); w.writerows(rows)
    return path

def generate(n=APPOINTMENTS, seed=SEED, out=ROOT/'data'):
    rng=random.Random(seed); out=Path(out); out.mkdir(parents=True,exist_ok=True)
    facilities=[]; docks=[]; yards=[]; carriers=[]; vehicles=[]; shifts=[]
    for i in range(1,FACILITIES+1):
        fid=f'FAC-{i:03}'; facilities.append(dict(facility_id=fid,name=f'Fulfillment Center {i:02}',city=['Chicago','Dallas','Atlanta','Seattle','Denver'][ (i-1)%5 ],timezone='America/Chicago',effective_from=iso(START),status='active'))
        for j in range(1,11):
            did=f'DOCK-{fid}-{j:03}'; typ=['standard','reefer','hazmat','mixed'][j%4]
            docks.append(dict(dock_id=did,facility_id=fid,dock_type=typ,hazmat_certified=str(typ in ('hazmat','mixed')).lower(),reefer_power=str(typ in ('reefer','mixed')).lower(),active='true'))
        for j in range(1,21): yards.append(dict(yard_slot_id=f'YARD-{fid}-{j:03}',facility_id=fid,slot_type='reefer' if j%8==0 else 'standard',capacity=1,active='true'))
        for j in range(1,6): carriers.append(dict(carrier_id=f'CAR-{i:03}-{j:02}',name=f'Carrier {i:02}-{j:02}',active='true'))
    for i,car in enumerate(carriers):
        for j in range(1,11):
            vehicles.append(dict(vehicle_id=f'VEH-{i+1:03}-{j:02}',carrier_id=car['carrier_id'],vehicle_type='tractor_trailer',capacity_pallets=rng.choice([24,28,32,36]),reefer_capable=str(j%3==0).lower(),hazmat_certified=str(j%4==0).lower(),active='true'))
    for day in range(DAYS):
        d=START+timedelta(days=day)
        for f in facilities:
            shifts.append(dict(labor_shift_id=f'SHIFT-{f["facility_id"]}-{d:%Y%m%d}',facility_id=f['facility_id'],shift_date=iso(d),start_time='06:00',end_time='22:00',team_count=12 if d.weekday()<5 else 7,active='true'))
    dock_by_fac=defaultdict(list); yard_by_fac=defaultdict(list); car_vehicles=defaultdict(list)
    for x in docks:dock_by_fac[x['facility_id']].append(x)
    for x in yards:yard_by_fac[x['facility_id']].append(x)
    for x in vehicles:car_vehicles[x['carrier_id']].append(x)
    # Reservations occupy every 30-minute dock and yard interval used by a service.
    occupied=set(); yard_occupied=set(); labor_used=Counter(); appts=[]; shipments=[]; reqs=[]; checkins=[]; exceptions=[]; events=[]; truths=[]
    anomaly_types=['overlapping_appointments','incompatible_load_assigned','checkin_before_appointment_date','labor_shift_unavailable','no_show_not_recorded']
    anomaly_ids={t:(max(1,n-5+i)) for i,t in enumerate(anomaly_types)} if n>=5 else {}
    for k in range(1,n+1):
        aid=f'APPT-2026-{k:06}'; sid=f'SHP-2026-{k:06}'; day_idx=rng.choices(range(DAYS),weights=[2 if day in (18,19,20,38,39,40,55,56,57) else 1 for day in range(DAYS)])[0]; d=START+timedelta(days=day_idx)
        fac=facilities[rng.randrange(FACILITIES)]; fid=fac['facility_id']; carrier=carriers[rng.randrange(len(carriers))]
        hazardous=(k%23==0); reefer=(k%7==0); direction='inbound' if k%2 else 'outbound'
        fleet=car_vehicles[carrier['carrier_id']]; compatible_vehicles=[v for v in fleet if (not hazardous or v['hazmat_certified']=='true') and (not reefer or v['reefer_capable']=='true')]
        veh=rng.choice(compatible_vehicles or fleet); pallets=rng.randint(8, min(veh['capacity_pallets'],36))
        reqid=f'REQ-{k:06}'; required='hazmat' if hazardous else ('reefer' if reefer else 'standard'); service=rng.choice([45,60,75,90]); win='06:00'; allocated=None
        for attempt in range(32):
            offset=attempt*30; startm=6*60+offset; ifday=d+timedelta(days=startm//1440); startm%=1440
            slot=f'{ifday.isoformat()}T{startm//60:02}:{startm%60:02}'; dock=rng.choice(dock_by_fac[fid]); yard_candidate=rng.choice(yard_by_fac[fid])
            span=max(1,(service+29)//30); dock_keys=[(dock['dock_id'],f'{(ifday+timedelta(minutes=startm+30*j)).isoformat()}T{((startm+30*j)%1440)//60:02}:{((startm+30*j)%60):02}') for j in range(span)]
            yard_keys=[(yard_candidate['yard_slot_id'],key[1]) for key in dock_keys]
            if not (set(dock_keys)&occupied) and not (set(yard_keys)&yard_occupied) and labor_used[(fid,ifday.isoformat())]<12*16 and (not hazardous or dock['hazmat_certified']=='true') and (not reefer or dock['reefer_power']=='true') and (not reefer or yard_candidate['slot_type']=='reefer') and (not hazardous or veh['hazmat_certified']=='true') and (not reefer or veh['reefer_capable']=='true'):
                occupied.update(dock_keys); yard_occupied.update(yard_keys); labor_used[(fid,ifday.isoformat())]+=1; allocated=(dock,ifday,startm,slot,yard_candidate); break
        if allocated is None:
            dock=dock_by_fac[fid][0]; appdate=d; startm=6*60+((k%32)*30); slot=f'{d.isoformat()}T{startm//60:02}:{startm%60:02}'; status='rejected_capacity'
        else: dock,appdate,startm,slot,yard=allocated; status='scheduled'
        # Explicit labeled anomalies are injected only into these rows; their labels explain expected rule response.
        anomaly=next((t for t,ix in anomaly_ids.items() if ix==k),None)
        if allocated is None: yard=yard_by_fac[fid][k%len(yard_by_fac[fid])]
        if anomaly=='overlapping_appointments':
            prior=next((a for a in appts if a['facility_id']==fid and a['status']=='scheduled' and ((not hazardous or next(x for x in docks if x['dock_id']==a['dock_id'])['hazmat_certified']=='true') and (not reefer or next(x for x in docks if x['dock_id']==a['dock_id'])['reefer_power']=='true'))),None)
            if prior:
                dock=next(x for x in docks if x['dock_id']==prior['dock_id']); appdate=date.fromisoformat(prior['appointment_date']); startm=int(prior['window_start'][:2])*60+int(prior['window_start'][3:]); slot=f'{appdate.isoformat()}T{prior["window_start"]}'; yard=next(x for x in yards if x['facility_id']==fid and x['yard_slot_id']!=prior['yard_slot_id'] and (not reefer or x['slot_type']=='reefer'))
            status='scheduled'; occupied.add((dock['dock_id'],slot))
        if anomaly=='incompatible_load_assigned':
            dock=dock_by_fac[fid][0]
            hazardous=True; required='hazmat'
        if anomaly=='labor_shift_unavailable':
            status='scheduled'
            for shift in shifts:
                if shift['facility_id']==fid and shift['shift_date']==iso(appdate): shift['active']='false'
        if anomaly=='no_show_not_recorded': status='no_show'
        shipments.append(dict(shipment_id=sid,facility_id=fid,carrier_id=carrier['carrier_id'],vehicle_id=veh['vehicle_id'],direction=direction,pallets=pallets,temperature_controlled=str(reefer).lower(),hazardous=str(hazardous).lower(),handling_requirement_id=reqid,requested_date=iso(d)))
        reqs.append(dict(handling_requirement_id=reqid,shipment_id=sid,required_dock_type=required,min_service_minutes=service,max_service_minutes=service+30,requires_reefer=str(reefer).lower(),requires_hazmat=str(hazardous).lower()))
        window_start=f'{startm//60:02}:{startm%60:02}'; endm=startm+max(60,service); window_end=f'{endm//60:02}:{endm%60:02}'
        appts.append(dict(appointment_id=aid,shipment_id=sid,facility_id=fid,carrier_id=carrier['carrier_id'],vehicle_id=veh['vehicle_id'],dock_id=dock['dock_id'],yard_slot_id=yard['yard_slot_id'],appointment_date=iso(appdate),window_start=window_start,window_end=window_end,service_minutes=service,status=status,scheduled_at=f'{iso(appdate)}T05:00:00'))
        base=dt(appdate,window_start); evseq=0
        evseq=0
        def event(kind, when, details=''):
            nonlocal evseq
            evseq+=1
            events.append(dict(event_id=f'EVT-{k:06}-{evseq:02}',appointment_id=aid,event_type=kind,event_time=when.isoformat(),source='simulator',details=details))
        event('request_created',dt(appdate,'05:00'), 'carrier request')
        event('appointment_decision',dt(appdate,'05:01'),status)
        if anomaly=='no_show_not_recorded':
            event('no_show_detected',base+timedelta(minutes=service+30),'no show; no check-in event expected')
            event('exception_raised',base+timedelta(minutes=service+30),'missing carrier check-in')
            event('appointment_closed',base+timedelta(minutes=service+30),'closed as no-show')
        else:
            earlylate=rng.choices([-20,-10,0,10,25],[5,10,65,15,5])[0]
            arrival=base+timedelta(minutes=earlylate)
            if anomaly=='checkin_before_appointment_date': arrival=base-timedelta(days=1)
            checkins.append(dict(checkin_id=f'CHECK-{aid}-01',appointment_id=aid,event_time=arrival.isoformat(),event_type='check_in',minutes_early_late=earlylate))
            event('check_in',arrival,'gate arrival')
            event('handling_completed',arrival+timedelta(minutes=10+service),'service completed')
            event('departed',arrival+timedelta(minutes=20+service),'departed facility')
        if anomaly:
            codes={'overlapping_appointments':'DOCK_CAPACITY','incompatible_load_assigned':'DOCK_COMPATIBILITY','checkin_before_appointment_date':'EARLY_DATE','labor_shift_unavailable':'LABOR_UNAVAILABLE','no_show_not_recorded':'NO_SHOW'}
            exceptions.append(dict(exception_id=f'EXC-{k:06}',appointment_id=aid,issue_type=anomaly,cause_code=codes[anomaly],severity='high',detected_at=dt(appdate,'05:02').isoformat(),resolution_status='open'))
            truths.append(dict(label_id=f'GT-{k:06}',appointment_id=aid,issue_type=anomaly,expected_decision='reject_or_flag',rule=codes[anomaly]))
    tables={'facilities':facilities,'docks':docks,'yard_slots':yards,'carriers':carriers,'vehicles':vehicles,'appointments':appts,'shipments':shipments,'labor_shifts':shifts,'handling_requirements':reqs,'checkin_events':checkins,'exceptions':exceptions,'events':events,'ground_truth':truths}
    for name,rows in tables.items(): dump_csv(out,name,rows)
    write_sqlite(out/'appointments.sqlite',tables)
    manifest={'seed':seed,'anchor_date':iso(START),'days':DAYS,'appointment_count':n,'generated_at_fixed':True,'files':{name:{'rows':len(rows),'sha256':hashlib.sha256((out/f'{name}.csv').read_bytes()).hexdigest()} for name,rows in tables.items()}}
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    checks=validate(tables)
    (out/'validation_summary.json').write_text(json.dumps(checks,indent=2),encoding='utf-8')
    if not checks['valid']: raise ValueError(f'Validation failed: {checks}')
    return manifest,checks

def write_sqlite(path,tables):
    if path.exists(): path.unlink()
    con=sqlite3.connect(path)
    con.execute('PRAGMA foreign_keys=ON')
    con.execute('PRAGMA journal_mode=OFF')
    con.execute('PRAGMA synchronous=OFF')
    primary={'facilities':'facility_id','docks':'dock_id','yard_slots':'yard_slot_id','carriers':'carrier_id','vehicles':'vehicle_id','shipments':'shipment_id','handling_requirements':'handling_requirement_id','labor_shifts':'labor_shift_id','appointments':'appointment_id','checkin_events':'checkin_id','exceptions':'exception_id','events':'event_id','ground_truth':'label_id'}
    foreign={'docks':[('facility_id','facilities','facility_id')],'yard_slots':[('facility_id','facilities','facility_id')],
             'vehicles':[('carrier_id','carriers','carrier_id')],'shipments':[('facility_id','facilities','facility_id'),('carrier_id','carriers','carrier_id'),('vehicle_id','vehicles','vehicle_id'),('handling_requirement_id','handling_requirements','handling_requirement_id')],
             'handling_requirements':[('shipment_id','shipments','shipment_id')],'labor_shifts':[('facility_id','facilities','facility_id')],
             'appointments':[('shipment_id','shipments','shipment_id'),('facility_id','facilities','facility_id'),('carrier_id','carriers','carrier_id'),('vehicle_id','vehicles','vehicle_id'),('dock_id','docks','dock_id'),('yard_slot_id','yard_slots','yard_slot_id')],
             'checkin_events':[('appointment_id','appointments','appointment_id')],'exceptions':[('appointment_id','appointments','appointment_id')],
             'events':[('appointment_id','appointments','appointment_id')],'ground_truth':[('appointment_id','appointments','appointment_id')]}
    for name,rows in tables.items():
        if not rows: continue
        cols=FIELDS[name]; constraints=[f'PRIMARY KEY ({primary[name]})']
        if name=='appointments': constraints.append('UNIQUE (shipment_id)')
        for col,parent,parent_col in foreign.get(name,[]):
            clause=f'FOREIGN KEY ({col}) REFERENCES {parent} ({parent_col}) DEFERRABLE INITIALLY DEFERRED'
            constraints.append(clause)
        con.execute(f'CREATE TABLE {name} ({", ".join(c+" TEXT" for c in cols)}, {", ".join(constraints)})')
    for name,rows in tables.items():
        if not rows: continue
        cols=FIELDS[name]
        con.executemany(f'INSERT INTO {name} VALUES ({",".join("?" for _ in cols)})',[[str(r.get(c,'')) for c in cols] for r in rows])
    fk_errors=con.execute('PRAGMA foreign_key_check').fetchall()
    if fk_errors: raise ValueError(f'SQLite foreign key errors: {fk_errors[:5]}')
    con.commit(); con.close()

def validate(t):
    errors=[]
    anomaly_types=['overlapping_appointments','incompatible_load_assigned','checkin_before_appointment_date','labor_shift_unavailable','no_show_not_recorded']
    def unique(name,key):
        vals=[r[key] for r in t[name]]
        if len(vals)!=len(set(vals)): errors.append(f'{name}.{key} is not unique')
    for n,k in [('facilities','facility_id'),('docks','dock_id'),('yard_slots','yard_slot_id'),('carriers','carrier_id'),('vehicles','vehicle_id'),('appointments','appointment_id'),('shipments','shipment_id'),('labor_shifts','labor_shift_id'),('handling_requirements','handling_requirement_id'),('checkin_events','checkin_id'),('exceptions','exception_id'),('events','event_id')]: unique(n,k)
    appt={r['appointment_id'] for r in t['appointments']}; ship={r['shipment_id'] for r in t['shipments']}; fac={r['facility_id'] for r in t['facilities']}; dock={r['dock_id'] for r in t['docks']}; yards={r['yard_slot_id'] for r in t['yard_slots']}; car={r['carrier_id'] for r in t['carriers']}; veh={r['vehicle_id'] for r in t['vehicles']}
    shipment_by={r['shipment_id']:r for r in t['shipments']}; dock_by={r['dock_id']:r for r in t['docks']}; vehicle_by={r['vehicle_id']:r for r in t['vehicles']}; yard_by={r['yard_slot_id']:r for r in t['yard_slots']}
    truth={r['appointment_id']:r['issue_type'] for r in t['ground_truth']}
    appt_by_id={r['appointment_id']:r for r in t['appointments']}
    if len(t['events']) != 5*len(t['appointments']): errors.append('event count does not reconcile to lifecycle records')
    for a in t['appointments']:
        if a['shipment_id'] not in ship or a['facility_id'] not in fac or a['dock_id'] not in dock or a['yard_slot_id'] not in yards or a['carrier_id'] not in car or a['vehicle_id'] not in veh: errors.append('appointment has invalid foreign key')
        if a['status'] not in {'scheduled','rejected_capacity','no_show'}: errors.append('appointment has invalid lifecycle status')
        source=shipment_by.get(a['shipment_id']); selected_dock=dock_by.get(a['dock_id']); selected_vehicle=vehicle_by.get(a['vehicle_id']); selected_yard=yard_by.get(a['yard_slot_id'])
        if source and (source['facility_id']!=a['facility_id'] or source['carrier_id']!=a['carrier_id'] or source['vehicle_id']!=a['vehicle_id']): errors.append('appointment relationship does not reconcile to shipment')
        if source and int(source['pallets'])>int(selected_vehicle['capacity_pallets']): errors.append('shipment pallets exceed vehicle capacity')
        anomaly=truth.get(a['appointment_id'])
        if source and a['status']=='scheduled' and anomaly!='incompatible_load_assigned':
            if source['hazardous']=='true' and (selected_dock['hazmat_certified']!='true' or selected_vehicle['hazmat_certified']!='true'): errors.append('hazmat capability mismatch')
            if source['temperature_controlled']=='true' and (selected_dock['reefer_power']!='true' or selected_vehicle['reefer_capable']!='true' or selected_yard['slot_type']!='reefer'): errors.append('reefer capability mismatch')
        try:
            if datetime.fromisoformat(a['appointment_date']+'T'+a['window_end']) <= datetime.fromisoformat(a['appointment_date']+'T'+a['window_start']): errors.append('appointment window end is not after start')
        except ValueError: errors.append('appointment has invalid date or time')
    for s in t['shipments']:
        if s['facility_id'] not in fac or s['carrier_id'] not in car or s['vehicle_id'] not in veh: errors.append('shipment has invalid foreign key')
        if s['direction'] not in {'inbound','outbound'}: errors.append('shipment has invalid direction')
    allowed_events={'request_created','appointment_decision','check_in','handling_completed','departed','no_show_detected','exception_raised','appointment_closed'}
    for e in t['events']:
        if e['appointment_id'] not in appt: errors.append('event has invalid appointment foreign key')
        if e['event_type'] not in allowed_events: errors.append('event has invalid type')
    for e in t['checkin_events']:
        if e['appointment_id'] not in appt: errors.append('check-in has invalid appointment foreign key')
        if truth.get(e['appointment_id'])!='checkin_before_appointment_date' and e['event_time'][:10] < appt_by_id[e['appointment_id']]['appointment_date']: errors.append('check-in occurred before appointment date without a ground-truth label')
    timeline=defaultdict(list)
    for e in t['events']: timeline[e['appointment_id']].append(e['event_time'])
    for appointment_id, times in timeline.items():
        if truth.get(appointment_id)!='checkin_before_appointment_date' and times!=sorted(times): errors.append('event lifecycle timestamps are out of order'); break
    expected=set(anomaly_types) if len(t['appointments'])>=5 else set()
    if set(truth.values()) != expected: errors.append('ground truth does not contain each expected anomaly exactly once')
    if len(t['exceptions']) != len(t['ground_truth']): errors.append('exception and ground truth counts do not reconcile')
    for e in t['events']+t['checkin_events']+t['exceptions']:
        if e['appointment_id'] not in appt: errors.append(f'{e} has invalid appointment foreign key'); break
    return {'valid':not errors,'errors':errors,'row_counts':{k:len(v) for k,v in t.items()},'ground_truth_labels':len(t['ground_truth'])}

def main():
    p=argparse.ArgumentParser(description='Generate deterministic synthetic dock appointment data')
    p.add_argument('--appointments',type=int,default=APPOINTMENTS); p.add_argument('--seed',type=int,default=SEED); p.add_argument('--out',type=Path,default=ROOT)
    a=p.parse_args(); manifest,checks=generate(a.appointments,a.seed,a.out)
    print(json.dumps({'output':str(a.out.resolve()),'manifest':manifest,'validation':checks},indent=2))
if __name__=='__main__': main()


