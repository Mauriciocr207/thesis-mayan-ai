import { BrowserRouter, Routes, Route } from "react-router"
import Home from "./pages/Home";
import Record from "./pages/Record";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/user/:userId" element={<Record />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;