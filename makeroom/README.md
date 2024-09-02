# Make Room !!!!

``` "Dead chic, so cool" ```

A little script that makes room by sorting files in subfolders, in a folder given as parameter.

## Usage example 

    python makeroom.py .\Documents\

## Result example 

Before making room :

```
C:\path\to\your\directory
│
├── vacation_photo.jpg
├── report.docx
├── presentation.pptx
├── song.mp3
├── movie.mp4
├── setup.exe
├── archive.zip
├── notes.txt
├── old_documents
│   ├── invoice.pdf
│   └── resume.docx
└── script.py
```

After: 

```
C:\path\to\your\directory
│
├── Images
│   └── vacation_photo.jpg
│
├── Documents
│   ├── report.docx
│   ├── presentation.pptx
│   └── notes.txt
│
├── Music
│   └── song.mp3
│
├── Videos
│   └── movie.mp4
│
├── Executables
│   └── setup.exe
│
├── Archives
│   └── archive.zip
│
├── Folders
│   └── old_documents
│       ├── invoice.pdf
│       └── resume.docx
│
└── Others
    └── script.py
```

## MIT License

For more details, see license file.


With ❤️, AE 2024