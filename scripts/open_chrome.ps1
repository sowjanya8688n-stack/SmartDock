param([int]$Port = 8000)

$url = "http://127.0.0.1:$Port/"
Start-Process "chrome.exe" $url
