
import React from "react";
import { useNavigate } from "react-router-dom";
import { useEffect } from "react";
import Form from "../form"; // Adjust the import path as necessary

const useAuth = () => {
  const navigate = useNavigate();
  useEffect(() => {
    const checkAuth = async () => {
      const response = await fetch("/api/@me", {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include", // Ensure cookies are sent with the request
      });
      
      
      
      console.log("Checking authentication", response);
      if (!response.ok) {
        console.log("Redirecting to login because not authenticated.");
        navigate("/login");
      }
    };
    checkAuth();
  }, [navigate]);
};


const ProtectedForm = () => {
  useAuth(); // This will redirect if not authenticated
  return <Form />;
};

export default ProtectedForm;
