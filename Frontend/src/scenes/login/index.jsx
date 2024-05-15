import React, { useState, useContext } from "react";
import { useNavigate } from "react-router-dom";
import {
  Box,
  Card,
  CardContent,
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
  // const response = await fetch("/api/login", {
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
        background: "#141B2D",
        height: "115vh", // Full viewport height
        display: "flex",
      }} // Use the background color from tokens
    >
      <Card sx={{ minWidth: 275, maxWidth: 400, bgcolor: "#1F2A40" }}>
        <CardContent>
          <Typography
            variant="h5"
            component="div"
            sx={{ mb: 2, color: colors.grey[100] }}
          >
            Login
          </Typography>
          <form onSubmit={handleSubmit}>
            <TextField
              fullWidth
              margin="normal"
              id="email"
              label="Email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              variant="outlined"
              sx={{ color: colors.grey[300] }}
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
            />
            <Button
              type="submit"
              variant="contained"
              color="primary"
              fullWidth
              sx={{ mt: 3 }}
            >
              Login
            </Button>
          </form>
        </CardContent>
      </Card>
    </Box>
  );
};

export default Login;
