'''
helper function to take token sent by facebook and verify it
If they match, allow the request, else return an error
'''
def verify_fb_token(token_sent):
    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return 'Invalid verification token'