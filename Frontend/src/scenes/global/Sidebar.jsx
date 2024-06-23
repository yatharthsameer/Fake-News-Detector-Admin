import React, { useState, useContext } from "react";
import {
  Box,
  IconButton,
  Typography,
  useTheme,
  Switch,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  useMediaQuery,
  Drawer,
} from "@mui/material";
import { useNavigate } from "react-router-dom";
import LightModeOutlinedIcon from "@mui/icons-material/LightModeOutlined";
import DarkModeOutlinedIcon from "@mui/icons-material/DarkModeOutlined";
import HomeOutlinedIcon from "@mui/icons-material/HomeOutlined";
import CalendarTodayOutlinedIcon from "@mui/icons-material/CalendarTodayOutlined";
import ReceiptOutlinedIcon from "@mui/icons-material/ReceiptOutlined";
import MenuOutlinedIcon from "@mui/icons-material/MenuOutlined";
import { ColorModeContext, tokens } from "../../theme";
import { AuthContext } from "../../context/AuthContext";

const Sidebar = () => {
  const theme = useTheme();
  const colors = tokens(theme.palette.mode);
  const isMobile = useMediaQuery(theme.breakpoints.down("sm"));
  const { isAuthenticated, setIsAuthenticated } = useContext(AuthContext);
  const colorMode = useContext(ColorModeContext);
  const navigate = useNavigate();
  const [isOpen, setIsOpen] = useState(false);
  const [selected, setSelected] = useState("Dashboard");

  const toggleDrawer = () => {
    setIsOpen(!isOpen);
  };

  const handleLogout = async () => {
    try {
      const response = await fetch("/api/logout", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include",
      });

      if (response.ok) {
        setIsAuthenticated(false);
        navigate("/login");
      } else {
        throw new Error("Failed to logout");
      }
    } catch (error) {
      console.error("Logout failed: ", error);
      alert("Logout failed.");
    }
  };

  const menuItems = [
    {
      title: "Search fact-checks",
      to: "/",
      icon: <HomeOutlinedIcon sx={{ color: "white" }} />,
    },
    {
      title: "Trends",
      to: "/trendspage",
      icon: <CalendarTodayOutlinedIcon sx={{ color: "white" }} />,
    },
    {
      title: "Add fact-check(s)",
      to: "/form",
      icon: <ReceiptOutlinedIcon sx={{ color: "white" }} />,
    },
  ];

  const drawerContent = (
    <Box
      sx={{
        width: 300,
        backgroundColor: "#26a450",
        height: "100%",
        display: "flex",
        flexDirection: "column",
        justifyContent: "space-between",
      }}
    >
      <Box>
        <Box
          sx={{
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            padding: "0px 0px",
          }}
        >
          <img
            alt="company-logo"
            src={`../../VNlogo.png`}
            style={{
              width: "100%",
              cursor: "pointer",
            }}
          />
        </Box>
        <Divider />
        <List>
          {menuItems.map((item) => (
            <ListItem
              button
              key={item.title}
              selected={selected === item.title}
              onClick={() => {
                setSelected(item.title);
                navigate(item.to);
                if (isMobile) {
                  toggleDrawer();
                }
              }}
              sx={{
                "&:hover": {
                  backgroundColor: colors.blueAccent[700],
                },
                margin: "20px 0px",
              }}
            >
              <ListItemIcon sx={{ color: "white" }}>{item.icon}</ListItemIcon>
              <ListItemText primary={item.title} />
            </ListItem>
          ))}
        </List>
      </Box>
      
    </Box>
  );

  return (
    <Box>
      {isMobile ? (
        <>
          <IconButton
            onClick={toggleDrawer}
            sx={{
              color: colors.grey[100],
              position: "absolute",
              top: 10,
              left: 10,
            }}
          >
            <MenuOutlinedIcon />
          </IconButton>
          <Drawer
            open={isOpen}
            onClose={toggleDrawer}
            anchor="left"
            ModalProps={{
              keepMounted: true,
            }}
          >
            {drawerContent}
          </Drawer>
        </>
      ) : (
        <Box
          sx={{
            width: 300,
            backgroundColor: "#26a450",
            height: "100vh",
            display: "flex",
            flexDirection: "column",
            justifyContent: "space-between",
            position: "fixed",
          }}
        >
          {drawerContent}
        </Box>
      )}
    </Box>
  );
};

export default Sidebar;
