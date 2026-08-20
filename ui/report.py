from datetime import date as _date


def generate_html_report(data: dict) -> str:
    inp = data["inputs"]
    res = data["results"]

    def _fmt_limit(val, unit: str) -> str:
        return f"{val:,.0f} {unit}" if val else "—"

    warnings_html = ""
    if data.get("warnings"):
        items = "".join(f"<li>{w}</li>" for w in data["warnings"])
        warnings_html = f'<div class="warn"><strong>⚠ Hinweise:</strong><ul>{items}</ul></div>'

    return f"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<title>Schnittdaten-Report — {data['project']}</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: Arial, Helvetica, sans-serif;
    font-size: 10.5pt;
    color: #1a1a1a;
  }}
  header {{
    background: #1a3c5e;
    color: #fff;
    padding: 18px 28px 14px;
  }}
  header h1 {{
    font-size: 17pt;
    font-weight: bold;
    letter-spacing: 0.02em;
  }}
  header .sub {{
    margin-top: 5px;
    font-size: 10pt;
    opacity: 0.88;
  }}
  .content {{
    padding: 22px 28px;
  }}
  h2 {{
    font-size: 11.5pt;
    color: #1a3c5e;
    border-bottom: 2px solid #1a3c5e;
    padding-bottom: 4px;
    margin: 22px 0 10px;
  }}
  table {{
    width: 100%;
    border-collapse: collapse;
  }}
  td {{
    padding: 5px 10px;
    border: 1px solid #d8d8d8;
    vertical-align: middle;
  }}
  td:first-child {{
    background: #f2f5f8;
    width: 52%;
    font-weight: bold;
    color: #333;
  }}
  .results td:last-child {{
    text-align: right;
    font-weight: bold;
    font-size: 11.5pt;
    color: #1a3c5e;
  }}
  .warn {{
    background: #fff8e1;
    border-left: 4px solid #f9a825;
    padding: 10px 14px;
    margin-top: 14px;
    font-size: 9.5pt;
  }}
  .warn ul {{ margin: 4px 0 0 18px; }}
  .formulas {{
    margin-top: 20px;
    padding: 10px 14px;
    background: #f7f7f7;
    border: 1px solid #ddd;
    font-size: 8.5pt;
    color: #555;
    line-height: 1.8;
  }}
  .formulas strong {{ color: #333; }}
  footer {{
    margin-top: 28px;
    border-top: 1px solid #ccc;
    padding: 8px 28px;
    font-size: 8pt;
    color: #888;
    text-align: center;
  }}
  @media print {{
    @page {{ margin: 15mm 18mm; }}
    header {{ -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
    .warn {{ -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
    td:first-child {{ -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
  }}
</style>
</head>
<body>
<header>
  <h1>Schnittdatenrechner — Fräsen</h1>
  <div class="sub">
    Projekt: <strong>{data['project']}</strong>
    &nbsp;&nbsp;|&nbsp;&nbsp;
    Datum: {data['date']}
  </div>
</header>

<div class="content">

  <h2>Eingaben</h2>
  <table>
    <tr><td>Werkstoff</td><td>{data['material']}</td></tr>
    <tr><td>Werkzeugdurchmesser D</td><td>{inp['D']:.1f} mm</td></tr>
    <tr><td>Schneidenzahl z</td><td>{inp['z']}</td></tr>
    <tr><td>Eckenradius r&epsilon;</td><td>{inp['re']:.2f} mm</td></tr>
    <tr><td>Schnittgeschwindigkeit v&#x2093;</td><td>{inp['vc']:.0f} m/min</td></tr>
    <tr><td>Zahnvorschub f&#x2093;</td><td>{inp['fz']:.3f} mm/z</td></tr>
    <tr><td>Schnitttiefe a&#x209A;</td><td>{inp['ap']:.2f} mm</td></tr>
    <tr><td>Schnittbreite a&#x2091;</td><td>{inp['ae']:.2f} mm</td></tr>
    <tr><td>Wirkungsgrad &eta;</td><td>{inp['eta']:.2f}</td></tr>
    <tr><td>Max. Spindeldrehzahl</td><td>{_fmt_limit(inp['n_max'], 'U/min')}</td></tr>
    <tr><td>Verfügbare Spindelleistung</td><td>{_fmt_limit(inp['P_max'], 'kW')}</td></tr>
  </table>

  <h2>Ergebnisse</h2>
  <table class="results">
    <tr><td>Drehzahl n</td><td>{res['n']:,.0f} U/min</td></tr>
    <tr><td>Tischvorschub v&#x2094;</td><td>{res['vf']:,.1f} mm/min</td></tr>
    <tr><td>Zeitspanvolumen Q</td><td>{res['Q']:.2f} cm&sup3;/min</td></tr>
    <tr><td>Schnittkraft F&#x2093;</td><td>{res['Fc']:.1f} N</td></tr>
    <tr><td>Schnittleistung P&#x2093;</td><td>{res['Pc']:.2f} kW</td></tr>
    <tr><td>Antriebsleistung P&#x2090;</td><td>{res['Pa']:.2f} kW</td></tr>
    <tr><td>Drehmoment M</td><td>{res['M']:.2f} Nm</td></tr>
    <tr><td>Max. Spanungsdicke h&#x2091;&#x2093;</td><td>{res['hex']:.3f} mm</td></tr>
    <tr><td>Rauheit R&#x2094; (theoretisch)</td><td>{res['Rz']:.1f} &micro;m</td></tr>
  </table>

  {warnings_html}

  <div class="formulas">
    <strong>Verwendete Formeln (DIN 6580/6584, Kienzle-Gleichung):</strong><br>
    n = (v&#x2093; &times; 1000) / (&pi; &times; D) &nbsp;&nbsp;|&nbsp;&nbsp;
    v&#x2094; = n &times; z &times; f&#x2093; &nbsp;&nbsp;|&nbsp;&nbsp;
    Q = (a&#x209A; &times; a&#x2091; &times; v&#x2094;) / 1000<br>
    k&#x2093; = k&#x2093;&#x2081;&#x2081; &times; h<sup>&minus;m&#x2093;</sup> &nbsp;&nbsp;|&nbsp;&nbsp;
    F&#x2093; = k&#x2093; &times; a&#x209A; &times; h &nbsp;&nbsp;|&nbsp;&nbsp;
    P&#x2093; = (F&#x2093; &times; v&#x2093;) / 60&thinsp;000 &nbsp;&nbsp;|&nbsp;&nbsp;
    P&#x2090; = P&#x2093; / &eta; &nbsp;&nbsp;|&nbsp;&nbsp;
    M = (F&#x2093; &times; D) / 2000
  </div>

</div>

<footer>
  Schnittdatenrechner &mdash; Richtwerte nach DIN&nbsp;6584 / Kienzle-Gleichung.
  Herstellerangaben und Maschinenfreigaben bleiben ma&szlig;geblich.
</footer>
</body>
</html>"""
