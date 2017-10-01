#TO-DO list:
    - Clean up unnecessary comments, debugging and code.
    - Change sync_files.sync_from_gdrive_to_local() so that it firstly stores the metadata for the directory that's being synced in a json file (using the method to be written in the previous to-do task), then after the metadata for the folder has been stored, we need to store the metadata for each file in the directory.
    - Change the sync_to_local() method, so that it only downloads the file if the local file is older than the remote file (check last modified date).
    - Add an option so that we can copy and paste the URL, and get back the auth code on a headless machine.
    - I got ot work out how to detect files that have been added, as it seems that "changes" don't include files that have been added - but I'm still investigating this..

