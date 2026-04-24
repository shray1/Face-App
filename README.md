# Face App

A cross-platform desktop application for face recognition, clustering, and identity management.

## Features

- Recursively scans a folder for images (JPG, PNG, BMP, TIFF, WebP, HEIC)
- Detects faces and extracts 128-d embeddings via `face_recognition` (dlib) or `deepface`
- Clusters faces into identities using DBSCAN
- PyQt6 GUI: person grid, per-person photo viewer, human-in-the-loop review dialog
- Stores all data in a local SQLite database (`~/.face_app/face_app.db`)

## Setup

```bash
pip install -e ".[dev]"
python main.py
```

## Requirements

- Python 3.10+
- CMake and a C++ compiler (for dlib / `face_recognition`)
- On Windows: Visual Studio Build Tools or VS 2022

## Project Structure

```
face_app/
├── db/          — SQLAlchemy models and session management
├── core/        — Image scanning, face detection, clustering
├── ui/          — PyQt6 windows and dialogs
└── utils/       — Image helpers, perceptual hashing
```
