from twilio.rest import Client

account_sid = 'replace with side'
auth_token = '[replace with auth token]'
client = Client(account_sid, auth_token)

message = client.messages.create(
  from_='whatsapp:+1', #NEEDS sender number
#   content_sid='HXb5b62575e6e4ff6129ad7c8efe1f983e',
#   content_variables='{"1":"12/1","2":"3pm"}',
  body='Hello! This is a test message from your healthcare platform.',
  media_url=['https://d9ae02825a48.ngrok-free.app/airemergency.png'],
to='whatsapp:+1' # NEEDS receiver number
)

print(message.sid)


