# Add a new MediaMimeType column
add_column(dbo, "media", "MediaMimeType", dbo.type_shorttext)
add_index(dbo, "media_MediaMimeType", "media", "MediaMimeType")
types = {
    "%jpg"           : "image/jpeg",
    "%jpeg"          : "image/jpeg",
    "%odt"           : "application/vnd.oasis.opendocument.text",
    "%pdf"           : "application/pdf",
    "%html"          : "text/html",
    "http%"          : "text/url"
}
for k, v in types.items():
    execute(dbo,"UPDATE media SET MediaMimeType = ? WHERE LOWER(MediaName) LIKE ?", (v, k))
execute(dbo,"UPDATE media SET MediaMimeType = 'application/octet-stream' WHERE MediaMimeType Is Null")