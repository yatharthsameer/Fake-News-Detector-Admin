import React, { useState, useContext } from "react";
import {
  Box,
  IconButton,
  Typography,
  useTheme,
  Switch,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  useMediaQuery,
} from "@mui/material";
import { Link, useNavigate } from "react-router-dom";
import ExitToAppIcon from "@mui/icons-material/ExitToApp";
import AnalyticsIcon from "@mui/icons-material/Analytics";
import SettingsIcon from "@mui/icons-material/Settings";
import LightModeOutlinedIcon from "@mui/icons-material/LightModeOutlined";
import DarkModeOutlinedIcon from "@mui/icons-material/DarkModeOutlined";
import HomeOutlinedIcon from "@mui/icons-material/HomeOutlined";
import PeopleOutlinedIcon from "@mui/icons-material/PeopleOutlined";
import ContactsOutlinedIcon from "@mui/icons-material/ContactsOutlined";
import ReceiptOutlinedIcon from "@mui/icons-material/ReceiptOutlined";
import PersonOutlinedIcon from "@mui/icons-material/PersonOutlined";
import CalendarTodayOutlinedIcon from "@mui/icons-material/CalendarTodayOutlined";
import HelpOutlineOutlinedIcon from "@mui/icons-material/HelpOutlineOutlined";
import BarChartOutlinedIcon from "@mui/icons-material/BarChartOutlined";
import PieChartOutlineOutlinedIcon from "@mui/icons-material/PieChartOutlineOutlined";
import TimelineOutlinedIcon from "@mui/icons-material/TimelineOutlined";
import MenuOutlinedIcon from "@mui/icons-material/MenuOutlined";
import MapOutlinedIcon from "@mui/icons-material/MapOutlined";
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
    { title: "Search fact-checks", to: "/", icon: <HomeOutlinedIcon /> },
    { title: "Trends", to: "/trendspage", icon: <CalendarTodayOutlinedIcon /> },
    { title: "Add fact-check(s)", to: "/form", icon: <ReceiptOutlinedIcon /> },
  ];

  const drawerContent = (
    <Box
      sx={{
        width: isMobile ? 250 : 300,
        backgroundColor: colors.primary[400],
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
            padding: "60px 20px",

          }}
        >
          <img
            alt="profile-user"
            width="40px"
            height="40px"
            src={`../../logo.jpeg`}
            style={{
              cursor: "pointer",
              borderRadius: "100%",
            }}
          />
          <Typography
            variant="h5"
            color={colors.grey[100]}
            fontWeight="bold"
            sx={{ ml: 2 }}
          >
            Misleading Data Predictor
          </Typography>
          <IconButton onClick={toggleDrawer} sx={{ ml: "auto" }}>
            <MenuOutlinedIcon />
          </IconButton>
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
              <ListItemIcon sx={{ color: colors.grey[100] }}>
                {item.icon}
              </ListItemIcon>
              <ListItemText primary={item.title} />
            </ListItem>
          ))}
        </List>
      </Box>
      <Box sx={{ padding: "10px 120px" }}>
        <Switch
          checked={theme.palette.mode === "dark"}
          onChange={colorMode.toggleColorMode}
          color="default"
          icon={<LightModeOutlinedIcon />}
          checkedIcon={<DarkModeOutlinedIcon />}
        />
       
         
      </Box>
    </Box>
  );

  return (
    <Box>
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
    </Box>
  );
};

export default Sidebar;
