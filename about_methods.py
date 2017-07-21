from apiclient import errors

def get_about_object(service):
    """
    Returns an "about" object (dict), that can query user info, email, etc..

    Args:
        service: authorized gdrive API service instance.
    """
    try:
        about = service.about().get().execute()
        return about
    except errors.HttpError as error:
        print('An error has occured: %s' % error)

def email_address(about_object):
    """
    Return the email address (string).

    Args:
        about_object: An "about" instance.
    """
    email = about_object['user']['emailAddress']
    return email

