#TO-DO list:
    - Clean up unnecessary comments, debugging and code, or alternatively, change all the debugging print statements, so that it uses the debug() method instead.
    - Change sync_files.sync_from_gdrive_to_local() so that it firstly stores the metadata for the directory that is being synced in a json file (using the method to be written in the previous to-do task), then after the metadata for the folder has been stored, we need to store the metadata for each file in the directory.
        - Im pretty sure that Im just going to shelve the data, instead of trying to store it in a json file, which I have done.
    - Change the sync_to_local() method, so that it only downloads the file if the local file is older than the remote file (check last modified date).
    - Add an option so that we can copy and paste the URL, and get back the auth code on a headless machine.
    - I got to work out how to detect files that have been added, as it seems that changes do not include files that have been added remotely - but I am still investigating this..

