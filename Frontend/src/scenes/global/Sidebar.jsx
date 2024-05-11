
import { useState, useContext, useEffect } from "react";
import { ProSidebar, Menu, MenuItem } from "react-pro-sidebar";
import { Box, IconButton, Typography, useTheme,Switch } from "@mui/material";
import { Link, useNavigate } from "react-router-dom";
import "react-pro-sidebar/dist/css/styles.css";
import ExitToAppIcon from "@mui/icons-material/ExitToApp";
import AnalyticsIcon from "@mui/icons-material/Analytics";
// import { tokens } from "../../theme";
import { ColorModeContext, tokens } from "../../theme";
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
import Login from "../login";
import { AuthContext } from '../../context/AuthContext';  // Import AuthContext

const Item = ({ title, to, icon, selected, setSelected }) => {
  const theme = useTheme();
  const colors = tokens(theme.palette.mode);
  const navigate = useNavigate();
const { isAuthenticated, setIsAuthenticated } = useContext(AuthContext);

  const handleClick = () => {
        setSelected(title);
        selected=title;

    if (!isAuthenticated && title === "Add fact check") {

      console.log("Unauthorized access attempt to Add fact check");
      return navigate("/login");
    }

    setSelected(title);
    navigate(to);
  };
      const handleLogout = async () => {
        try {
          const response = await fetch(
            "/logout",
            {
              method: "POST",
              headers: {
                "Content-Type": "application/json",
              },
              credentials: "include",
            }
          );

          if (response.ok) {
            // Update the logout logic as necessary
            navigate("/login");
          } else {
            throw new Error("Failed to logout");
          }
        } catch (error) {
          console.error("Logout failed: ", error);
          alert("Logout failed.");
        }
      };

  return (
    <MenuItem
      active={selected === title}
      style={{ color: colors.grey[100] }}
      onClick={handleClick}
      icon={icon}
    >
      <Typography>{title}</Typography>
    </MenuItem>
  );
};

const Sidebar = () => {
  const { isAuthenticated, setIsAuthenticated } = useContext(AuthContext);

  const colorMode = useContext(ColorModeContext);
  const theme = useTheme();
    const handleColorModeToggle = () => {
    colorMode.toggleColorMode(); // Toggle light/dark mode
  }; 
   const navigate = useNavigate();


  const colors = tokens(theme.palette.mode);
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [selected, setSelected] = useState("Dashboard");

const handleLogout = async () => {
  console.log("Logging out");

  try {
    const response = await fetch(
      "/api/logout",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include", // Ensure cookies are sent with the request
      }
    );
    
    if (response.ok) {
      setIsAuthenticated(false); // Make sure to set authentication to false
      navigate("/login");
    }
    else {
      throw new Error("Failed to logout");
    }
   
  }
  catch (error) {
   
      alert("Failed to logout");
    
      navigate("/login");
  }
};

  return (
    <Box
      sx={{
        height: "120vh", // Full viewport height
        display: "flex",
        
        "& .pro-sidebar-inner": {
          background: `${colors.primary[400]} !important`,
        },
        "& .pro-icon-wrapper": {
          backgroundColor: "transparent !important",
        },
        "& .pro-inner-item": {
          padding: "5px 35px 5px 20px !important",
        },
        "& .pro-inner-item:hover": {
          color: "#868dfb !important",
        },
        "& .pro-menu-item.active": {
          color: "#6870fa !important",
        },
      }}
    >
      <ProSidebar collapsed={isCollapsed}>
        <Menu iconShape="square">
          {/* LOGO AND MENU ICON */}
          <MenuItem
            onClick={() => setIsCollapsed(!isCollapsed)}
            icon={isCollapsed ? <MenuOutlinedIcon /> : undefined}
            style={{
              margin: "10px 0 20px 0",
              color: colors.grey[100],
            }}
          ></MenuItem>

          {!isCollapsed && (
            <Box display="flex" alignItems="center" mb="25px">
              <Box ml="35px">
                <img
                  alt="profile-user"
                  width="40px"
                  height="40px"
                  src={`../../logo.jpeg`}
                  style={{ cursor: "pointer", borderRadius: "100%" }}
                />
              </Box>
              <Box flex="1" ml="10px">
                <Typography
                  variant="h5"
                  color={colors.grey[100]}
                  fontWeight="bold"
                  sx={{ m: "0" }}
                >
                  Misleading Data
                </Typography>
                <Typography
                  variant="h5"
                  color={colors.grey[100]}
                  fontWeight="bold"
                  sx={{ m: "0" }}
                >
                  Predictor
                </Typography>
              </Box>
              <Box mr="20px">
                <IconButton onClick={() => setIsCollapsed(!isCollapsed)}>
                  <MenuOutlinedIcon />
                </IconButton>
              </Box>
            </Box>
          )}
          <Box paddingLeft={isCollapsed ? undefined : "10%"} mt="70px">
            <Item
              title="Search fact-checks"
              to="/"
              icon={<HomeOutlinedIcon />}
              selected={selected}
              setSelected={setSelected}
            />
            <Item
              title="Add fact check"
              to="/form"
              icon={<ReceiptOutlinedIcon />}
              selected={selected}
              setSelected={setSelected}
            />
            {/* <Item
              title="Settings"
              to="/faq"
              icon={<SettingsIcon />}
              selected={selected}
              setSelected={setSelected}
            />{" "} */}
            {/* <MenuItem
              icon={<PersonOutlinedIcon />}
              style={{ color: colors.grey[100] }}
              onClick={handleLogout} // Directly attach logout functionality here
            >
              <Typography>Log out</Typography>
            </MenuItem> */}
          </Box>
        </Menu>
        <Box
          sx={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            backgroundColor: colors.primary[400],
            height: "auto", // Auto height
            paddingTop: isCollapsed ? "303px" : "250px", // Adjust the padding based on the collapse state
            paddingBottom: "10px", // Add padding to separate user info and switch
            transition: "padding-top 0.3s", // Add smooth transition for padding change
          }}
        >
          <Switch
            checked={theme.palette.mode === "dark"}
            onChange={handleColorModeToggle}
            color="default"
            icon={<LightModeOutlinedIcon />} // Icon for light mode
            checkedIcon={<DarkModeOutlinedIcon />} // Icon for dark mode
          />
        </Box>
      </ProSidebar>
    </Box>
  );
};

export default Sidebar;