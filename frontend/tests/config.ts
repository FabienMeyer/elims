export const config = {
  baseURL: process.env.BASE_URL || "http://localhost:5173",
  apiURL: process.env.VITE_API_URL || "http://localhost:8000",
  mailcatcherURL: process.env.MAILCATCHER_HOST || "http://localhost:1080",
}

export default config
