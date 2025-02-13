import React, { useState, useContext } from "react";
import {
  Box,
  IconButton,
  Divider,
  useTheme,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  useMediaQuery,
  Drawer,
  FormControlLabel,
  Switch,
} from "@mui/material";
import { useNavigate } from "react-router-dom";
import HomeOutlinedIcon from "@mui/icons-material/HomeOutlined";
import CalendarTodayOutlinedIcon from "@mui/icons-material/CalendarTodayOutlined";
import ReceiptOutlinedIcon from "@mui/icons-material/ReceiptOutlined";
import MenuOutlinedIcon from "@mui/icons-material/MenuOutlined";
import { ColorModeContext, tokens } from "../../theme";
import { AuthContext } from "../../context/AuthContext";
import { useTranslation } from "react-i18next";

const Sidebar = () => {
  const theme = useTheme();
  const colors = tokens(theme.palette.mode);
  const isMobile = useMediaQuery(theme.breakpoints.down("sm"));
  const { isAuthenticated, setIsAuthenticated } = useContext(AuthContext);
  const colorMode = useContext(ColorModeContext);
  const navigate = useNavigate();
  const { i18n } = useTranslation(); // Translation hook
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

  const handleLanguageToggle = () => {
    const newLanguage = i18n.language === "en" ? "hi" : "en";
    i18n.changeLanguage(newLanguage);
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
    {
      title: "Download Dataset",
      to: "/downloadDataset",
      icon: <ReceiptOutlinedIcon sx={{ color: "white" }} />,
    },
    {
      title: "About",
      to: "/about",
      icon: <ReceiptOutlinedIcon sx={{ color: "white" }} />,
    },
  ];

  const drawerContent = (
    <Box
      sx={{
        width: isMobile ? "50vw" : 300, // Set the width based on screen size
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
              width: "90%",
              paddingTop: "20px",
              cursor: "pointer",
            }}
            onClick={() => navigate("/")}
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
      <Box
        sx={{
          padding: "20px",
          textAlign: "center",
        }}
      >
        <FormControlLabel
          control={
            <Switch
              checked={i18n.language === "hi"}
              onChange={handleLanguageToggle}
              color="primary"
            />
          }
          label={i18n.language === "en" ? "ENGLISH" : "HINDI"}
          labelPlacement="top"
          sx={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
          }}
        />
      </Box>
    </Box>
  );

  return (
    <Box>
      {isMobile ? (
        <>
          <Box
            sx={{
              display: "flex",
              alignItems: "center",
              position: "absolute",
              top: 10,
              left: 10,
            }}
          >
            <IconButton onClick={toggleDrawer} sx={{ color: colors.grey[100] }}>
              <MenuOutlinedIcon />
            </IconButton>
            <img
              alt="company-logo"
              src={`../../VNlogoWhite.png`}
              style={{
                marginLeft: 10, // Adjust spacing between icon and logo
                width: 140, // Adjust the size of the logo as needed
                height: 50,
                cursor: "pointer",
              }}
              onClick={() => navigate("/")}
            />
            <Box sx={{ display: "flex", alignItems: "center" }}>
              <FormControlLabel
                control={
                  <Switch
                    checked={i18n.language === "hi"}
                    onChange={handleLanguageToggle}
                    sx={{
                      "& .MuiSwitch-thumb": {
                        backgroundColor: "black", // Force the toggle thumb to be black on mobile
                      },
                      "& .MuiSwitch-track": {
                        backgroundColor: "grey !important", // Keep the switch track grey even when toggled
                        opacity: 1, // Ensure the track remains visible in both states
                      },
                    }}
                  />
                }
                label={i18n.language === "en" ? "ENGLISH" : "HINDI"}
                sx={{
                  color: "black", // Force the label text color to be black on mobile
                  "@media (min-width: 600px)": {
                    color: "inherit", // Revert to default color on larger screens
                  },
                }}
              />
            </Box>
          </Box>

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
