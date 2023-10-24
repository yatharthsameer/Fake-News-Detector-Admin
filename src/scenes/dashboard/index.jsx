import {
  Box,
  Button,
  IconButton,
  Typography,
  useTheme,
  TextField,
  InputLabel,
  FormControl,
  Select,
  MenuItem,
} from "@mui/material";
import { tokens } from "../../theme";
import { mockTransactions, mockNewsData } from "../../data/mockData";
import DownloadOutlinedIcon from "@mui/icons-material/DownloadOutlined";
import EmailIcon from "@mui/icons-material/Email";
import PointOfSaleIcon from "@mui/icons-material/PointOfSale";
import PersonAddIcon from "@mui/icons-material/PersonAdd";
import TrafficIcon from "@mui/icons-material/Traffic";
import Header from "../../components/Header";
import LineChart from "../../components/LineChart";
import GeographyChart from "../../components/GeographyChart";
import BarChart from "../../components/BarChart";
import StatBox from "../../components/StatBox";
import ProgressCircle from "../../components/ProgressCircle";
import React, { useContext } from "react";

const Dashboard = () => {
  const theme = useTheme();
  const colors = tokens(theme.palette.mode);
  const [searchType, setSearchType] = React.useState("text"); // Default search type is "text"

  const handleSearchTypeChange = (event) => {
    setSearchType(event.target.value);
  };
  const handleSearchButtonClick = () => {
    // Handle the search button click here
    // You can access the search type using the `searchType` state
    // and the search input value from the text field
  };
  return (
    <Box m="20px">
      {/* HEADER */}

      <Box display="flex" justifyContent="space-between" alignItems="center">
        <Header title="DASHBOARD" subtitle="Welcome to your dashboard" />

        <Box>
          <Button
            sx={{
              backgroundColor: colors.blueAccent[600],
              color: colors.grey[100],
              fontSize: "14px",
              fontWeight: "bold",
              padding: "10px 20px",
            }}
          >
            <DownloadOutlinedIcon sx={{ mr: "10px" }} />
            Download Reports
          </Button>
        </Box>
      </Box>
      <Box display="flex" justifyContent="center" alignItems="center" mb="20px">
        <FormControl
          variant="outlined"
          size="medium"
          style={{
            marginRight: "8px",
            width: "150px",
            backgroundColor: colors.primary[400],
          }} // Increase width of the dropdown
        >
          <InputLabel>Search Type</InputLabel>
          <Select
            value={searchType}
            onChange={handleSearchTypeChange}
            label="Search Type"
          >
            <MenuItem value="text">Text</MenuItem>
            <MenuItem value="image">Image</MenuItem>
            <MenuItem value="link">Link</MenuItem>
          </Select>
        </FormControl>

        <TextField
          variant="outlined"
          label="Search"
          size="medium"
          fullWidth
          InputProps={{
            style: {
              backgroundColor: colors.primary[400],

              borderRadius: "20px", // Rounded corners
            },
          }}
        />
        <Button
          variant="contained"
          onClick={handleSearchButtonClick}
          sx={{
            backgroundColor: colors.blueAccent[600],
            color: colors.grey[100],
            borderRadius: "8px",
            marginLeft: "10px",

            fontSize: "14px",
            fontWeight: "bold",
            padding: "10px 20px",
          }}
        >
          Search
        </Button>
      </Box>

      {/* GRID & CHARTS */}
      <Box
        display="grid"
        gridTemplateColumns="repeat(12, 1fr)"
        gridAutoRows="140px"
        gap="20px"
      >
        {/* ROW 1
        <Box
          gridColumn="span 3"
          backgroundColor={colors.primary[400]}
          display="flex"
          alignItems="center"
          justifyContent="center"
        >
          <StatBox
            title="12,361"
            subtitle="Emails Sent"
            progress="0.75"
            increase="+14%"
            icon={
              <EmailIcon
                sx={{ color: colors.greenAccent[600], fontSize: "26px" }}
              />
            }
          />
        </Box>
        <Box
          gridColumn="span 3"
          backgroundColor={colors.primary[400]}
          display="flex"
          alignItems="center"
          justifyContent="center"
        >
          <StatBox
            title="431,225"
            subtitle="Sales Obtained"
            progress="0.50"
            increase="+21%"
            icon={
              <PointOfSaleIcon
                sx={{ color: colors.greenAccent[600], fontSize: "26px" }}
              />
            }
          />
        </Box>
        <Box
          gridColumn="span 3"
          backgroundColor={colors.primary[400]}
          display="flex"
          alignItems="center"
          justifyContent="center"
        >
          <StatBox
            title="32,441"
            subtitle="New Clients"
            progress="0.30"
            increase="+5%"
            icon={
              <PersonAddIcon
                sx={{ color: colors.greenAccent[600], fontSize: "26px" }}
              />
            }
          />
        </Box>
        <Box
          gridColumn="span 3"
          backgroundColor={colors.primary[400]}
          display="flex"
          alignItems="center"
          justifyContent="center"
        >
          <StatBox
            title="1,325,134"
            subtitle="Traffic Received"
            progress="0.80"
            increase="+43%"
            icon={
              <TrafficIcon
                sx={{ color: colors.greenAccent[600], fontSize: "26px" }}
              />
            }
          />
        </Box> */}
        {/* ROW 3 */}
        <Box
          gridColumn="span 5"
          gridRow="span 2"
          backgroundColor={colors.primary[400]}
          p="30px"
        >
          <Typography variant="h5" fontWeight="600">
            False News
          </Typography>
          <Box
            display="flex"
            flexDirection="column"
            alignItems="center"
            mt="25px"
          >
            <ProgressCircle size="125" />
            <Typography
              variant="h5"
              color={colors.greenAccent[100]}
              sx={{ mt: "15px" }}
            >
              Accuracy{" "}
            </Typography>
            <Typography
              sx={{
                fontSize: "13px", // Adjust the desired font size
              }}
            >
              Disclaimer: This site uses AI technology for decision-making. We
              are not liable for AI decisions but commit to correcting any
              errors with valid proof.
            </Typography>
          </Box>
        </Box>
        {/* <Box
          gridColumn="span 4"
          gridRow="span 2"
          backgroundColor={colors.primary[400]}
        >
          <Typography
            variant="h5"
            fontWeight="600"
            sx={{ padding: "30px 30px 0 30px" }}
          >
            Sales Quantity
          </Typography>
          <Box height="250px" mt="-20px">
            <BarChart isDashboard={true} />
          </Box>
        </Box> */}
        <Box
          gridColumn="span 7"
          gridRow="span 4"
          backgroundColor={colors.primary[400]}
          overflow="auto"
        >
          <Box
            display="flex"
            justifyContent="space-between"
            alignItems="center"
            borderBottom={`1px solid ${colors.primary[400]}`}
            colors={colors.grey[100]}
            p="15px"
          >
            <Typography
              color={colors.grey[100]}
              variant="h5"
              fontWeight="600"
              sx={{ mt: "15px" }}
            >
              Top Matches 
            </Typography>
          </Box>
          {Object.entries(mockNewsData).map(([index, newsItem]) => (
            <Box
              key={`${newsItem.Story_URL}-${index}`}
              display="flex"
              flexDirection="row"
              alignItems="flex-start"
              borderBottom={`1px solid ${colors.primary[400]}`}
              p=" 8px 35px"
            >
              <img
                src={newsItem.image} // Use the image URL from your data
                alt="News"
                width="110px" // Set the width and height to create a square
                height="95px"
                style={{ marginRight: "20px" }} // Add some spacing between image and content
              />
              <div>
                <Typography
                  color={colors.greenAccent[100]}
                  variant="h5"
                  fontWeight="600"
                >
                  <a
                    href={newsItem.Story_URL}
                    target="_blank"
                    rel="noopener noreferrer"
                    style={{
                      color: colors.greenAccent[100],
                      textDecoration: "none",
                    }} // Add some spacing between image and content
                  >
                    {newsItem.Headline}
                  </a>
                </Typography>
                <Typography color={colors.grey[100]}>
                  {newsItem.Story_Date}
                </Typography>
                <Typography color={colors.grey[100]}>
                  {/* Read More */}
                  98% match
                </Typography>
              </div>
            </Box>
          ))}
        </Box>

        <Box
          gridColumn="span 5"
          gridRow="span 2"
          backgroundColor={colors.primary[400]}
        >
          <Box
            mt="22px"
            p="0 30px"
            display="flex "
            justifyContent="space-between"
            alignItems="center"
          >
            <Box>
              <Typography
                variant="h5"
                fontWeight="600"
                color={colors.grey[100]}
              >
                Timeline
              </Typography>
              {/* <Typography
                variant="h3"
                fontWeight="bold"
                color={colors.greenAccent[500]}
              >
                $59,342.32
              </Typography> */}
            </Box>
            <Box>
              <IconButton>
                <DownloadOutlinedIcon
                  sx={{ fontSize: "26px", color: colors.greenAccent[100] }}
                />
              </IconButton>
            </Box>
          </Box>
          <Box height="250px" m="-20px 0 0 0">
            <LineChart isDashboard={true} />
          </Box>
        </Box>
      </Box>
    </Box>
  );
};

export default Dashboard;
