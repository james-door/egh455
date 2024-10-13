import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter, Routes, Route, Navigate} from "react-router-dom";
import "./styles/global.css"

import VideoFeed from './pages/VideoFeed.js';
import AirQuality from './pages/AirQuality.js';

import IdentifiedTargets from './pages/IdentifiedTargets.js'; 
import DataLog from './pages/DataLog.js';


import NoPage from './pages/404.js';
import NavBar from './Componets/Navbar.js';
import NotificationManager from './Componets/NotificationManager.js';
const root = ReactDOM.createRoot(document.getElementById('root'));

root.render(
  <div>
    <NotificationManager/>
    <BrowserRouter>
      <NavBar/>
      <Routes>
        <Route path="/" element={<Navigate to="/Video Feed" replace />} />
        <Route path="/Video Feed" element={<VideoFeed />}/>
        <Route path="/Air Quality" element={<AirQuality />}/>
        <Route path="/Identified Targets" element={<IdentifiedTargets />}/>
        <Route path="/Data Log" element={<DataLog />}/>

      </Routes>
    </BrowserRouter>
  </div>
);

