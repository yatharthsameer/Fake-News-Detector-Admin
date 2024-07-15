import React, { useState, useContext } from "react";
import { useNavigate } from "react-router-dom";
import {
  Box,
  Card,
  TextField,
  Button,
  Typography,
  useTheme,
} from "@mui/material";
import { ColorModeContext, tokens } from "../../theme"; // Ensure that tokens and ColorModeContext are correctly imported
import { AuthContext } from "../../context/AuthContext"; // Assuming you have an AuthContext

const Login = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();
  const theme = useTheme();
  const colors = tokens(theme.palette.mode); // Fetch the appropriate color tokens based on the theme

  const { setIsAuthenticated } = useContext(AuthContext); // Using context to set authentication status

  const handleSubmit = async (event) => {
    event.preventDefault();
    const response = await fetch("/api/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
      credentials: "include", // Make sure credentials include is set
    });
    if (response.ok) {
      setIsAuthenticated(true); // Set authentication to true upon successful login
      setTimeout(() => navigate("/form"), 1000); // Delay navigation to allow cookie handling
    } else {
      alert("Please check your email and password and try again.");
      console.error("Failed to log in");
    }
  };

  return (
    <Box
      display="flex"
      alignItems="center"
      justifyContent="center"
      sx={{
        height: "100vh", // Full viewport height
      }}
    >
      <Card
        sx={{
          width: "60%", // Adjust width as needed
          display: "flex",
          flexDirection: "row",
          alignItems: "center",
          backgroundColor: "white",
          padding: 4,
          borderRadius: 2,
          boxShadow: 3,
        }}
      >
        <Box
          sx={{
            flex: 1,
            display: "flex",
            flexDirection: "column",
            alignItems: "flex-start",
            justifyContent: "center",
            paddingLeft: 4,
          }}
        >
          <img
            alt="Vishvas News Logo"
            src="./logoVN.png" // Replace with actual logo path
            style={{
              width: "200px",
              height: "auto",
              marginBottom: "20px",
              marginLeft: "-20px",
            }} // Adjusted logo size
          />
          <Typography
            variant="h3" // Adjusted variant for bigger size
            component="div"
            sx={{ mb: 1, color: "black", fontWeight: "bold" }}
          >
            Login
          </Typography>
          <Typography
            variant="subtitle2" // Adjusted variant for smaller size
            component="div"
            sx={{ mb: 2, color: "gray" }} // Changed color to gray for better readability
          >
            to continue to Login
          </Typography>
        </Box>
        <Box sx={{ flex: 1 }}>
          <form onSubmit={handleSubmit}>
            <TextField
              fullWidth
              margin="normal"
              id="email"
              label="Email id"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              variant="outlined"
              sx={{
                "& .MuiOutlinedInput-root": {
                  "& fieldset": {
                    borderColor: "#e5e5e5",
                  },
                  "&:hover fieldset": {
                    borderColor: "#e5e5e5",
                  },
                  "&.Mui-focused fieldset": {
                    borderColor: "#e5e5e5",
                  },
                  "& input": {
                    color: "black", // Input text color
                  },
                },
                "& .MuiInputLabel-root": {
                  color: "black",
                },
              }}
            />
            <TextField
              fullWidth
              margin="normal"
              id="password"
              label="Password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              variant="outlined"
              sx={{
                "& .MuiOutlinedInput-root": {
                  "& fieldset": {
                    borderColor: "#e5e5e5",
                  },
                  "&:hover fieldset": {
                    borderColor: "#e5e5e5",
                  },
                  "&.Mui-focused fieldset": {
                    borderColor: "#e5e5e5",
                  },
                  "& input": {
                    color: "black", // Input text color
                  },
                },
                "& .MuiInputLabel-root": {
                  color: "black",
                },
              }}
            />
            <Button
              type="submit"
              variant="contained"
              fullWidth
              sx={{
                mt: 3,
                backgroundColor: "#26a450",
                color: "white",
                borderRadius: 25, // Adjust border radius for rounded button
              }}
            >
              LOGIN
            </Button>
          </form>
        </Box>
      </Card>
    </Box>
  );
};

export default Login;
