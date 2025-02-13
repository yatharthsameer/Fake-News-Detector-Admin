// src/App.js
import { useState } from "react";
import { Routes, Route } from "react-router-dom";
import Sidebar from "./scenes/global/Sidebar";
import Dashboard from "./scenes/dashboard";

// import Line from "./scenes/line";

import { CssBaseline, ThemeProvider, Button } from "@mui/material";
import { ColorModeContext, useMode } from "./theme";
import Login from './scenes/login';
import { AuthProvider } from './context/AuthContext';
import Trendspage from "./scenes/trendspage";
import ProtectedForm from './scenes/protectedForm';
import About from './scenes/about';
import DownloadDataset from './scenes/downloadDataset';
import { useTranslation } from "react-i18next";

function App() {
  const [theme, colorMode] = useMode();
  const [isSidebar] = useState(true);
  const { i18n } = useTranslation(); // Translation hook

  const toggleLanguage = () => {
    // Toggle between 'en' and 'hi'
    const newLanguage = i18n.language === 'en' ? 'hi' : 'en';
    i18n.changeLanguage(newLanguage);
  };

  return (
    <AuthProvider>
      <ColorModeContext.Provider value={colorMode}>
        <ThemeProvider theme={theme}>
          <CssBaseline />
          <div className="app">
            <Sidebar isSidebar={isSidebar} />
            <main className="content">


              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/login" element={<Login />} />
                <Route path="/form" element={<ProtectedForm />} />
                <Route path="/trendspage" element={<Trendspage />} />
                <Route path="/downloadDataset" element={<DownloadDataset />} />
                <Route path="/about" element={<About />} />
              </Routes>
            </main>
          </div>
        </ThemeProvider>
      </ColorModeContext.Provider>
    </AuthProvider>
  );
}

export default App;
