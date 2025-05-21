# RubberDuck Droid Web

This is a Next.js web app that provides an AI chat interface using the [nlux](https://docs.nlkit.com/nlux) React component, configured with the LangChain adapter to connect to the FastAPI backend at `/droid`.

## Features
- Modern Next.js (App Router, TypeScript, Tailwind CSS)
- AI chat UI powered by nlux
- LangChain adapter for backend integration
- Connects to FastAPI backend at `/droid`

## Getting Started

1. Install dependencies:
   ```bash
   npm install
   ```
2. Run the development server:
   ```bash
   npm run dev
   ```
3. Open [http://localhost:3000](http://localhost:3000) in your browser.

## Backend
Make sure your FastAPI server (see `serve.py`) is running and accessible at `/droid` on the same host or configure the endpoint as needed.

## Customization
- Edit the chat UI in `src/app/page.tsx`.
- See [nlux documentation](https://docs.nlkit.com/nlux) for advanced usage.

---
