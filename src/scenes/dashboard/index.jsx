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
  const [results, setResults] = React.useState([]);
  const [chartData, setChartData] = React.useState([]);

  const theme = useTheme();
  const colors = tokens(theme.palette.mode);
  const [searchType, setSearchType] = React.useState("text"); // Default search type is "text"
  const searchInputRef = React.useRef(null);
  const [isSearchInitiated, setIsSearchInitiated] = React.useState(false);

  const handleSearchTypeChange = (event) => {
    setSearchType(event.target.value);
  };
  const processChartData = (matches) => {
    let yearCount = {};

    matches.forEach((match) => {
      if (match.percentage > 20) {
        const year = match.data.Story_Date.split(" ").slice(-1)[0]; // Extract the year from the date
        yearCount[year] = (yearCount[year] || 0) + 1;
      }
    });

    const minYear = Math.min(...Object.keys(yearCount).map(Number)) - 5;
    const maxYear = Math.max(...Object.keys(yearCount).map(Number)) + 5;

    for (let year = minYear; year <= maxYear; year++) {
      if (!yearCount[year]) {
        yearCount[year] = 0;
      }
    }

    const chartData = {
      id: "queryFrequency",
      color: tokens("dark").blueAccent[300],
      data: Object.keys(yearCount)
        .map((year) => ({
          x: year,
          y: yearCount[year],
        }))
        .sort((a, b) => a.x - b.x), // Ensure that data is sorted by year
    };

    return [chartData];
  };

  const handleSearchButtonClick = () => {
    // Extract the search type (already available in the searchType state)
    // Get the search query from the TextField (let's give it a ref to easily access its value)
    setIsSearchInitiated(true);

    const searchQuery = searchInputRef.current.value;

    // Make a POST request to the Flask server
    fetch("http://localhost:3001/search", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ query: searchQuery }),
    })
      .then((response) => response.json())
      .then((data) => {
        console.log(data); // For now, let's just log the top matches returned by the server
        setResults(data);
        setChartData(processChartData(data));
      })
      .catch((error) => {
        console.error("Error fetching data:", error);
      });
  };
  // const handleReadMoreClick = () => {
  //   const searchQuery = searchInputRef.current.value;

  //   // Make a POST request to the Flask server
  //   fetch("http://localhost:3001/searchAll", {
  //     method: "POST",
  //     headers: {
  //       "Content-Type": "application/json",
  //     },
  //     body: JSON.stringify({ query: searchQuery }),
  //   })
  //     .then((response) => response.json())
  //     .then((data) => {
  //       console.log(data); // Log the data returned by the server
  //     })
  //     .catch((error) => {
  //       console.error("Error fetching data:", error);
  //     });
  // };

  const highestMatch = results.length > 0 ? results[0].percentage : 0;

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
          inputRef={searchInputRef} // Attach the ref to the input inside TextField
          variant="outlined"
          label="Search"
          size="medium"
          fullWidth
          InputProps={{
            style: {
              backgroundColor: colors.primary[400],

              borderRadius: "8px", // Rounded corners
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
        {isSearchInitiated && (
          <>
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
                <ProgressCircle size="125" progress={highestMatch / 100} />
                <Typography
                  variant="h5"
                  color={colors.greenAccent[100]}
                  sx={{ mt: "15px" }}
                >
                  Accuracy
                </Typography>
                <Typography
                  sx={{
                    fontSize: "13px", // Adjust the desired font size
                  }}
                >
                  Disclaimer: This site uses AI technology for decision-making.
                  We are not liable for AI decisions but commit to correcting
                  any errors with valid proof.
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
                {/* <Button
                  variant="outlined"
                  color="primary"
                  onClick={handleReadMoreClick}
                >
                  Read More
                </Button> */}
              </Box>
              {results.map((result, index) => (
                <Box
                  key={index}
                  display="flex"
                  flexDirection="row"
                  alignItems="flex-start"
                  borderBottom={`1px solid ${colors.primary[400]}`}
                  p=" 13px 35px"
                >
                  <img
                    src={result.data.img} // Display the image from the result
                    alt="News"
                    width="110px"
                    height="95px"
                    style={{ marginRight: "20px" }}
                  />
                  {/* Display other details from the result like the image, headline, etc.
                 You can also display the matching percentage using result.percentage */}
                  <div>
                    <Typography
                      color={colors.greenAccent[100]}
                      variant="h5"
                      fontWeight="600"
                    >
                      <a
                        href={result.data.Story_URL}
                        target="_blank"
                        rel="noopener noreferrer"
                        style={{
                          color: colors.greenAccent[100],
                          textDecoration: "none",
                        }}
                      >
                        {result.data.Headline}
                      </a>
                    </Typography>
                    <Typography color={colors.grey[100]}>
                      {result.data.Story_Date}
                    </Typography>
                    <Typography color={colors.grey[100]}>
                      {result.percentage}% match
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
                <LineChart data={chartData} isDashboard={true} />
              </Box>
            </Box>
          </>
        )}
      </Box>
    </Box>
  );
};

export default Dashboard;
