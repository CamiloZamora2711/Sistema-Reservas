from email.message import EmailMessage
from email.utils import make_msgid
import smtplib

msg = EmailMessage()
msg['Subject'] = 'Test'
logo_cid = make_msgid()

msg.set_content("Plain text")
msg.add_alternative(f"""\
<html>
    <body>
        <img src="cid:{logo_cid[1:-1]}">
        <p>Test!</p>
    </body>
</html>
""", subtype='html')

print("OK so far")
try:
    with open('static/descarga.png', 'rb') as f:
        img_data = f.read()
    msg.get_payload()[1].add_related(img_data, 'image', 'png', cid=logo_cid)
    print("Added related image successfully")
except Exception as e:
    print("Error:", e)
