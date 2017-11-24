#TO-DO list:
    - Clean up unnecessary comments, debugging and code, or alternatively, change all the debugging print statements, so that it uses the debug() method instead.
    - Change the sync_to_local() method, so that it only downloads the file if the local file is older than the remote file (check last modified date).
    - Add an option so that we can copy and paste the URL, and get back the auth code on a headless machine.
    - store the metadata in sqlite3.
    - watch local files for changes (inotify?).


#Daily tasks:
    - the change object does return files that have been added, so now I just have to use the 'largestChangeId' or 'newStartPageToken', so I know where the next change begins...
