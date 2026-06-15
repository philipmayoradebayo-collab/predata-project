// Auth.jsx — AgroSense NG Login & Register
import { useState } from "react"
import axios from "axios"

const API = "https://predata-project.onrender.com"

export default function Auth({ onLogin }) {
  const [mode, setMode]       = useState("login")  // "login" or "register"
  const [loading, setLoading] = useState(false)
  const [error, setError]     = useState(null)
  const [form, setForm]       = useState({
    full_name: "", email: "", phone: "",
    state: "", farm_size: "", password: ""
  })

  const handle = e => setForm({ ...form, [e.target.name]: e.target.value })

  const submit = async () => {
    setLoading(true); setError(null)
    try {
      if (mode === "register") {
        const res = await axios.post(`${API}/auth/register`, form)
        alert("Registration successful! Please login.")
        setMode("login")
      } else {
        const res = await axios.post(`${API}/auth/login`, {
          email: form.email,
          password: form.password
        })
        localStorage.setItem("user", JSON.stringify(res.data.user))
        localStorage.setItem("token", res.data.token)
        onLogin(res.data.user)
      }
    } catch (e) {
      setError(e.response?.data?.detail || "Something went wrong")
    }
    setLoading(false)
  }

  return (
    <div style={{
      minHeight: "100vh",
      background: "linear-gradient(135deg, #e8f5e9 0%, #f1f8e9 50%, #e0f2f1 100%)",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      padding: "1rem",
      fontFamily: "'Segoe UI', sans-serif"
    }}>
      <div style={{
        background: "white",
        borderRadius: "16px",
        padding: "2rem",
        width: "100%",
        maxWidth: "420px",
        boxShadow: "0 8px 32px rgba(0,0,0,0.1)"
      }}>
        {/* Logo */}
        <div style={{textAlign:"center", marginBottom:"1.5rem"}}>
          <div style={{fontSize:"3rem"}}>🌿</div>
          <h1 style={{color:"#2d6a4f", fontSize:"1.5rem", fontWeight:"700"}}>
            AgroSense NG
          </h1>
          <p style={{color:"#888", fontSize:"0.85rem"}}>
            AI-Powered Farm Assistant
          </p>
        </div>

        {/* Tabs */}
        <div style={{
          display:"flex", marginBottom:"1.5rem",
          background:"#f5f5f5", borderRadius:"8px", padding:"4px"
        }}>
          <button onClick={() => setMode("login")} style={{
            flex:1, padding:"0.5rem",
            background: mode === "login" ? "#2d6a4f" : "transparent",
            color: mode === "login" ? "white" : "#666",
            border:"none", borderRadius:"6px",
            cursor:"pointer", fontWeight:"600", fontSize:"0.9rem"
          }}>Login</button>
          <button onClick={() => setMode("register")} style={{
            flex:1, padding:"0.5rem",
            background: mode === "register" ? "#2d6a4f" : "transparent",
            color: mode === "register" ? "white" : "#666",
            border:"none", borderRadius:"6px",
            cursor:"pointer", fontWeight:"600", fontSize:"0.9rem"
          }}>Register</button>
        </div>

        {/* Form */}
        {mode === "register" && (
          <div style={{marginBottom:"1rem"}}>
            <label style={{fontSize:"0.8rem", color:"#555", display:"block", marginBottom:"0.3rem"}}>
              Full Name
            </label>
            <input
              name="full_name" value={form.full_name} onChange={handle}
              placeholder="e.g. Adebayo Mayowa"
              style={{width:"100%", padding:"0.6rem", borderRadius:"8px",
                border:"1px solid #ddd", fontSize:"0.9rem", outline:"none",
                boxSizing:"border-box"}}
            />
          </div>
        )}

        <div style={{marginBottom:"1rem"}}>
          <label style={{fontSize:"0.8rem", color:"#555", display:"block", marginBottom:"0.3rem"}}>
            Email Address
          </label>
          <input
            name="email" value={form.email} onChange={handle}
            placeholder="e.g. farmer@gmail.com" type="email"
            style={{width:"100%", padding:"0.6rem", borderRadius:"8px",
              border:"1px solid #ddd", fontSize:"0.9rem", outline:"none",
              boxSizing:"border-box"}}
          />
        </div>

        {mode === "register" && (
          <>
            <div style={{marginBottom:"1rem"}}>
              <label style={{fontSize:"0.8rem", color:"#555", display:"block", marginBottom:"0.3rem"}}>
                Phone Number
              </label>
              <input
                name="phone" value={form.phone} onChange={handle}
                placeholder="e.g. 08012345678"
                style={{width:"100%", padding:"0.6rem", borderRadius:"8px",
                  border:"1px solid #ddd", fontSize:"0.9rem", outline:"none",
                  boxSizing:"border-box"}}
              />
            </div>

            <div style={{marginBottom:"1rem"}}>
              <label style={{fontSize:"0.8rem", color:"#555", display:"block", marginBottom:"0.3rem"}}>
                Your State
              </label>
              <select
                name="state" value={form.state} onChange={handle}
                style={{width:"100%", padding:"0.6rem", borderRadius:"8px",
                  border:"1px solid #ddd", fontSize:"0.9rem", outline:"none",
                  boxSizing:"border-box"}}
              >
                <option value="">Select your state</option>
                {["Abia","Adamawa","AkwaIbom","Anambra","Bauchi",
                  "Bayelsa","Benue","Borno","CrossRiver","Delta",
                  "Ebonyi","Edo","Ekiti","Enugu","FCT","Gombe",
                  "Imo","Jigawa","Kaduna","Kano","Katsina","Kebbi",
                  "Kogi","Kwara","Lagos","Nasarawa","Niger","Ogun",
                  "Ondo","Osun","Oyo","Plateau","Rivers","Sokoto",
                  "Taraba","Yobe","Zamfara"
                ].map(s => <option key={s} value={s}>{s}</option>)}
              </select>
            </div>

            <div style={{marginBottom:"1rem"}}>
              <label style={{fontSize:"0.8rem", color:"#555", display:"block", marginBottom:"0.3rem"}}>
                Farm Size
              </label>
              <select
                name="farm_size" value={form.farm_size} onChange={handle}
                style={{width:"100%", padding:"0.6rem", borderRadius:"8px",
                  border:"1px solid #ddd", fontSize:"0.9rem", outline:"none",
                  boxSizing:"border-box"}}
              >
                <option value="">Select farm size</option>
                <option value="Less than 1 hectare">Less than 1 hectare</option>
                <option value="1 - 5 hectares">1 - 5 hectares</option>
                <option value="5 - 10 hectares">5 - 10 hectares</option>
                <option value="10 - 50 hectares">10 - 50 hectares</option>
                <option value="More than 50 hectares">More than 50 hectares</option>
              </select>
            </div>
          </>
        )}

        <div style={{marginBottom:"1.5rem"}}>
          <label style={{fontSize:"0.8rem", color:"#555", display:"block", marginBottom:"0.3rem"}}>
            Password
          </label>
          <input
            name="password" value={form.password} onChange={handle}
            placeholder="Enter password" type="password"
            style={{width:"100%", padding:"0.6rem", borderRadius:"8px",
              border:"1px solid #ddd", fontSize:"0.9rem", outline:"none",
              boxSizing:"border-box"}}
          />
        </div>

        {error && (
          <div style={{
            background:"#fdecea", border:"1px solid #f44336",
            borderRadius:"8px", padding:"0.75rem",
            color:"#c62828", fontSize:"0.85rem", marginBottom:"1rem"
          }}>
            ❌ {error}
          </div>
        )}

        <button onClick={submit} disabled={loading} style={{
          width:"100%", padding:"0.75rem",
          background: loading ? "#aaa" : "#2d6a4f",
          color:"white", border:"none", borderRadius:"8px",
          fontSize:"1rem", fontWeight:"700", cursor:"pointer"
        }}>
          {loading ? "Please wait..." : mode === "login" ? "🔐 Login" : "✅ Create Account"}
        </button>

        <p style={{textAlign:"center", marginTop:"1rem", fontSize:"0.85rem", color:"#888"}}>
          {mode === "login" ? "Don't have an account? " : "Already have an account? "}
          <span
            onClick={() => setMode(mode === "login" ? "register" : "login")}
            style={{color:"#2d6a4f", cursor:"pointer", fontWeight:"600"}}
          >
            {mode === "login" ? "Register here" : "Login here"}
          </span>
        </p>

        {/* USSD Note */}
        <div style={{
          marginTop:"1.5rem", padding:"0.75rem",
          background:"#e8f5e9", borderRadius:"8px",
          textAlign:"center", fontSize:"0.8rem", color:"#2d6a4f"
        }}>
          📱 Smallholder farmer? No login needed!<br/>
          <a href="https://agrosense-ussd.vercel.app" target="_blank"
             style={{color:"#2d6a4f", fontWeight:"600"}}>
            Use USSD Simulator →
          </a>
        </div>
      </div>
    </div>
  )
}