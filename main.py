from flask import Flask, request, render_template_string, jsonify
import datetime
import requests
import json

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Don't leave yet!</title>
  <style>
    body { font-family: monospace; background:#000; color:#0f0; padding:15px; line-height:1.5; margin:0; }
    h1 { color:#0f0; margin:0 0 15px; }
    h2 { color:#0f0; margin:25px 0 8px; }
    pre { background:#111; padding:10px; border:1px solid #222; white-space:pre-wrap; word-break:break-all; margin:8px 0; font-size:13px; }
    #log { max-height:280px; overflow-y:auto; background:#000; padding:10px; border:1px solid #333; margin:15px 0; font-size:13px; }
    button { background:#002200; color:#0f0; border:1px solid #0f0; padding:8px 16px; margin:6px 10px 6px 0; cursor:pointer; }
    button:hover { background:#004400; }
    .section { margin-bottom:20px; }
  </style>
</head>
<body>

<h1>Welcome, Eren Tunahan UÇAR!</h1>

<div class="section">
  <h2>About You:</h2>
  <pre id="server-info">{{ server_info }}</pre>
</div>

<div class="section">
  <h2>Information Your Browser Gave Us:</h2>
  <pre id="client-info">Yükleniyor... (ekran, RAM tahmini, CPU çekirdek, batarya vb.)</pre>
</div>

<script>
// Tarayıcı bilgileri topla
function getClientInfo() {
  const nav = navigator;
  const scr = screen;
  const conn = nav.connection || {};

  let batteryInfo = "Batarya bilgisi yok";
  if (nav.getBattery) {
    nav.getBattery().then(b => {
      batteryInfo = `Batarya: %${Math.round(b.level * 100)} (${b.charging ? "şarj oluyor" : "şarjda değil"}, kalan süre tahmini: ${b.dischargingTime === Infinity ? "bilinmiyor" : b.dischargingTime + " sn"})`;
      document.getElementById('client-info').textContent += `\n${batteryInfo}`;
    }).catch(() => {});
  }

  return {
    userAgent: nav.userAgent,
    platform: nav.platform || '—',
    languages: nav.languages?.join(', ') || nav.language || '—',
    cookieEnabled: nav.cookieEnabled,
    onLine: nav.onLine,
    timezone: Intl.DateTimeFormat().resolvedOptions().timeZone || '—',
    screen: `${scr.width} × ${scr.height} (piksel oranı: ${window.devicePixelRatio.toFixed(2)})`,
    windowInner: `${window.innerWidth} × ${window.innerHeight}`,
    colorDepth: `${scr.colorDepth} bit`,
    hardwareConcurrency: nav.hardwareConcurrency || 'bilinmiyor',
    deviceMemory: nav.deviceMemory ? `${nav.deviceMemory} GB (yaklaşık)` : 'bilinmiyor',
    connection: conn.effectiveType ? `${conn.effectiveType} (${conn.downlink || '?'} Mbps)` : 'bilinmiyor',
    battery: batteryInfo,
    vendor: nav.vendor || '—',
    maxTouchPoints: nav.maxTouchPoints || '—'
  };
}

// Bilgileri göster + sunucuya gönder
function collectAndSend() {
  const info = getClientInfo();
  document.getElementById('client-info').textContent = JSON.stringify(info, null, 2);

  fetch('/log-client', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(info)
  })
  .catch(err => console.error('Gönderme hatası:', err));
}

window.addEventListener('load', () => {
  collectAndSend();  // otomatik ilk toplama
});
</script>

</body>
</html>
"""

@app.route('/')
def index():
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Sunucu tarafı bilgiler
    ip = request.remote_addr
    ua = request.headers.get('User-Agent', '—')
    headers = dict(request.headers)

    # Yaklaşık konum
    geo = {'city': '—', 'country': '—', 'lat': '?', 'lon': '?', 'isp': '—'}
    try:
        r = requests.get(f"http://ip-api.com/json/{ip}", timeout=5)
        d = r.json()
        if d.get('status') == 'success':
            geo.update({
                'city': d.get('city', '—'),
                'country': d.get('country', '—'),
                'lat': d.get('lat', '?'),
                'lon': d.get('lon', '?'),
                'isp': d.get('isp', '—')
            })
    except:
        pass

    server_info = f"""Zaman: {now}
IP Adresi: {ip}
User-Agent (tam): {ua}
Tahmini Tarayıcı/OS: {request.user_agent.browser or '?'} {request.user_agent.version or '?'} on {request.user_agent.platform or '?'}
Dil Tercihi: {request.headers.get('Accept-Language', '—')}
Yaklaşık Konum: {geo['city']}, {geo['country']}  ({geo['lat']}, {geo['lon']})
ISP: {geo['isp']}

Tüm Header'lar:
{json.dumps(headers, indent=2, ensure_ascii=False)}
"""

    print(f"[ZİYARET {now}] IP: {ip} | UA: {ua[:80]}...")
    data = {
        "content": f"""
    IP: {ip}
    UA: {ua}
    Browser: {request.user_agent.browser or '?'}
    Version: {request.user_agent.version or '?'}
    Platform: {request.user_agent.platform or '?'}
    Konum: {geo['city']}, {geo['country']} ({geo['lat']}, {geo['lon']})
    ISP: {geo['isp']}
    """
    }
  
    return render_template_string(HTML_TEMPLATE, server_info=server_info)

@app.route('/log-client', methods=['POST'])
def log_client():
    data = request.json
    print("\n[CLIENT INFO]")
    print(json.dumps(data, indent=2, ensure_ascii=False))
    print("-" * 60)
    return jsonify({"message": "Tarayıcı bilgileri konsola loglandı"})

if __name__ == '__main__':
    app.run()
