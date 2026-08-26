import ReactDOM from "react-dom/client";
import App from "./App.tsx";
import "./styles/index.css";
import { HeroUIProvider } from "@heroui/react";
import { ToastProvider } from "@heroui/toast";

ReactDOM.createRoot(document.getElementById("root") as HTMLElement).render(
  <HeroUIProvider>
    <ToastProvider />
    <App />
  </HeroUIProvider>
);
