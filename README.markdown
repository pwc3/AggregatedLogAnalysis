iOS Aggregated Log Parser
-------------------------

On your iOS device, go to:

    Settings > General > About > Diagnostics & Usage > Diagnostic & Usage Data

There will be eight entries beginning with `log-aggregated` followed by the datestamp. If you long-tap one of the files, you'll see the whole filename:

    log-aggregated-2014-01-07-191504_iPhone-5s.plist.synced

Select one of the the `log-aggregated` files. This will show a long XML Property List file.

Select the contents of the file. Unfortunately, there is no *Select All* option here, so you need to drag from the top of the file to the bottom of the file. Start dragging from the top left. This is a bit tricky, but if you drag your finger to just the right spot on the bottom right of the screen, the contents of the document will select and scroll quickly by. Once you select the entire document, select *Copy*.

Paste the contents of the file into an email and send it to yourself. I find it useful to include the date as the subject of the message.

On your desktop machine, copy the XML Property List contents from the email body and paste it into a new text file. If you're copying the log for `2014-01-07`, then name the file `2014-01-07.plist`. The filename doesn't matter, but it should end in `.plist`.

