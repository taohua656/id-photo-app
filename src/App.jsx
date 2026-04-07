import React, { useState } from 'react';
import { PayPalScriptProvider, PayPalButtons } from "@paypal/react-paypal-js";
import { motion } from 'framer-motion';


const API_URL = import.meta.env.VITE_API_URL;
const PAYPAL_CLIENT_ID = import.meta.env.VITE_PAYPAL_CLIENT_ID;

function App() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [resultUrl, setResultUrl] = useState(null);
  const [loading, setLoading] = useState(false);
  const [bgColor, setBgColor] = useState("#FFFFFF");
  const [sizePreset, setSizePreset] = useState("us_passport");
  const [orderId, setOrderId] = useState(null);

  const handleFileChange = (e) => {
    const selected = e.target.files[0];
    if (selected) {
      setFile(selected);
      setPreview(URL.createObjectURL(selected));
      setResultUrl(null);
    }
  };

  const createPreOrder = async () => {
    const res = await fetch(`${API_URL}/create-order`, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({ size_preset: sizePreset, bg_color: bgColor })
    });
    const data = await res.json();
    return data.order_id;
  };

  const generatePhoto = async () => {
    if (!file) return;
    setLoading(true);

    const formData = new FormData();
    formData.append("file", file);
    formData.append("color", bgColor);
    formData.append("size", sizePreset);

    try {
      const response = await fetch(`${API_URL}/generate`, {
        method: "POST",
        body: formData,
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        setResultUrl(url);
      }
    } catch (error) {
      console.error("Error:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <nav className="bg-white border-b border-gray-200">
        <div className="max-w-5xl mx-auto px-4 h-16 flex items-center">
          <span className="text-xl font-bold text-gray-800">AI ID Photo Maker</span>
        </div>
      </nav>

      <main className="flex-grow container mx-auto px-4 py-12">
        <div className="text-center mb-10">
          <h1 className="text-4xl font-extrabold text-gray-900 mb-4">
            Professional ID Photos in Seconds
          </h1>
          <p className="text-lg text-gray-600">AI-powered background removal for passports, visas, and resumes</p >
        </div>

        <div className="max-w-xl mx-auto bg-white rounded-2xl shadow-xl p-6">
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">Upload Photo</label>
            <input type="file" accept="image/*" onChange={handleFileChange} className="block w-full text-sm" />
          </div>

          {preview && (
            <>
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">Document Type</label>
                <select value={sizePreset} onChange={(e) => setSizePreset(e.target.value)} className="block w-full p-2 border rounded">
                  <option value="us_passport">US Passport (2x2 in)</option>
                  <option value="schengen_visa">Schengen Visa (35x45 mm)</option>
                  <option value="resume">Resume (Standard)</option>
                </select>
              </div>

              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">Background Color</label>
                <div className="flex gap-4">
                  <button onClick={() => setBgColor("#FFFFFF")} className="w-10 h-10 rounded-full bg-white border"></button>
                  <button onClick={() => setBgColor("#4383BF")} className="w-10 h-10 rounded-full bg-[#4383BF] border"></button>
                  <button onClick={() => setBgColor("#D92B2B")} className="w-10 h-10 rounded-full bg-[#D92B2B] border"></button>
                </div>
              </div>

              <button onClick={generatePhoto} disabled={loading} className="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold">
                {loading ? "Processing..." : "Generate Photo"}
              </button>
            </>
          )}

          {resultUrl && (
            <div className="text-center mt-6">
              <h3 className="text-xl font-bold text-green-600 mb-4">Photo Ready!</h3>
              < img src={resultUrl} alt="Result" className="h-64 mx-auto rounded-lg shadow-md mb-6" />
              
              <PayPalScriptProvider options={{ "client-id": PAYPAL_CLIENT_ID }}>
                <PayPalButtons 
                  createOrder={async () => {
                    const tempOrderId = await createPreOrder();
                    setOrderId(tempOrderId);
                    return tempOrderId;
                  }}
                  onApprove={async (data) => {
                    await fetch(`${API_URL}/activate-order`, {
                      method: "POST",
                      headers: {"Content-Type": "application/json"},
                      body: JSON.stringify({ order_id: data.orderID })
                    });
                    
                    const link = document.createElement('a');
                    link.href = resultUrl;
                    link.download = 'id_photo.jpg';
                    link.click();
                  }}
                />
              </PayPalScriptProvider>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

export default App;
