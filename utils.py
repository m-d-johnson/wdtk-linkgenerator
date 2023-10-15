def send_email(recipient, body):
    import smtplib
    import ssl

    smtp_server = "localhost"
    port = 1025  # For starttls
    sender_email = "TODO"
    password = "TODO"

    # Try to log in to server and send email
    try:
        server = smtplib.SMTP(smtp_server, port)
        server.login(sender_email, password)
        # Send Email
        receiver_email = recipient  # Enter receiver address
        sender_email = "TODO"
        server.sendmail(sender_email, receiver_email, body)
    except Exception as e:
        # Print any error messages to stdout
        print(e)
    finally:
        server.quit()
