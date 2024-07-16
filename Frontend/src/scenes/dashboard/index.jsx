import {
  Box,
  Button,
  IconButton,
  Typography,
  useTheme,
  TextField,
  CircularProgress,
  useMediaQuery,
  Grid,
  ButtonBase,
  Radio,
  RadioGroup,
  FormControlLabel,
  InputLabel,
  FormControl,
  MenuItem,
  FormLabel,
} from "@mui/material";
import DownloadOutlinedIcon from "@mui/icons-material/DownloadOutlined";
import CloseIcon from "@mui/icons-material/Close";
import React, { useEffect, useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import Header from "../../components/Header";
import LineChart from "../../components/LineChart";
import ProgressCircle from "../../components/ProgressCircle";
import { tokens } from "../../theme";

const Dashboard = () => {
  const theme = useTheme();
  const colors = tokens(theme.palette.mode);
  const isXs = useMediaQuery(theme.breakpoints.down("xs"));
  const isSm = useMediaQuery(theme.breakpoints.down("sm"));
  const isMd = useMediaQuery(theme.breakpoints.down("md"));

  const [results, setResults] = useState([]);
  const [chartData, setChartData] = useState([]);
  const [imageUrl, setImageUrl] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(5);
  const [apiCallCompleted, setApiCallCompleted] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedImageFile, setSelectedImageFile] = useState(null);
  const [selectedImagePreview, setSelectedImagePreview] = useState(null);
  const [isSearchInitiated, setIsSearchInitiated] = useState(false);
  const [searchType, setSearchType] = useState("text");

  const searchInputRef = React.useRef(null);
  const urlInputRef = React.useRef(null);

  const indexOfLastItem = currentPage * itemsPerPage;
  const indexOfFirstItem = indexOfLastItem - itemsPerPage;
  const currentItems = results.slice(indexOfFirstItem, indexOfLastItem);

  const handleNext = () => {
    setCurrentPage(currentPage + 1);
  };

  const handlePrev = () => {
    setCurrentPage(currentPage - 1);
  };

  const handleSearchTypeChange = (event) => {
    setSearchType(event.target.value);
  };

  const processChartData = (matches) => {
    let yearCount = {};

    matches.forEach((match) => {
      if (match.percentage > 20) {
        const year = match.data.Story_Date.split(" ").slice(-1)[0];
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
      id: "Frequency",
      color: tokens("dark").blueAccent[300],
      data: Object.keys(yearCount)
        .map((year) => ({
          x: year,
          y: yearCount[year],
        }))
        .sort((a, b) => a.x - b.x),
    };

    return [chartData];
  };

  const handleSearchEnterKey = (event) => {
    if (event.key === "Enter") {
      handleSearchButtonClick();
    }
  };

  const handleSearchButtonClick = () => {
    setIsLoading(true);
    setIsSearchInitiated(true);

    if (searchType === "text") {
      const searchQuery = searchInputRef.current.value;
      // fetch("https://factcheckerbtp.vishvasnews.com/api/ensemble", {
      fetch("/api/ensemble", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          charset: "utf-8",
        },
        body: JSON.stringify({ query: searchQuery }),
      })
        .then((response) => response.json())
        .then((data) => {
          setIsLoading(false);
          if (data.error) {
            setErrorMessage(data.error);
            setApiCallCompleted(true);
          } else {
            setResults(data);
            setChartData(processChartData(data));
            setApiCallCompleted(true);
            setErrorMessage(false);
          }
        })
        .catch((error) => {
          setIsLoading(false);
          setErrorMessage(
            "The server encountered some issue, please click search again."
          );
          setApiCallCompleted(true);
        });
    } else if (searchType === "image" && selectedImageFile) {
      const formData = new FormData();
      formData.append("file", selectedImageFile);

      fetch("/api/upload", {
        method: "POST",
        body: formData,
      })
        .then((response) => response.json())
        .then((data) => {
          setIsLoading(false);
          setResults(data);
          setChartData(processChartData(data));
          setApiCallCompleted(true);
        })
        .catch((error) => {
          setIsLoading(false);
          setErrorMessage(
            "The server encountered some issue, please click search again."
          );
          setApiCallCompleted(true);
        });
    } else if (searchType === "link" && imageUrl.trim()) {
      const imgURLQ = imageUrl.trim();

      fetch("/api/uploadImageURL", {
    //  fetch("https://factcheckerbtp.vishvasnews.com/api/uploadImageURL", {
      // fetch("http://localhost:8080/api/uploadImageURL", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          charset: "utf-8",
        },
        body: JSON.stringify({ image_url: imgURLQ }),
      })
        .then((response) => response.json())
        .then((data) => {
          setIsLoading(false);
          setResults(data);
          setChartData(processChartData(data));
          setApiCallCompleted(true);
        })
        .catch((error) => {
          setIsLoading(false);
                    setApiCallCompleted(true);

          setErrorMessage(error.message);
        });
    }
  };

  const onDrop = useCallback((acceptedFiles) => {
    const file = acceptedFiles[0];
    setSelectedImageFile(file);
    const reader = new FileReader();
    reader.onload = (e) => {
      setSelectedImagePreview(e.target.result);
    };
    reader.readAsDataURL(file);
  }, []);

  const { getRootProps, getInputProps } = useDropzone({
    onDrop,
    accept: "image/*",
  });

  const handleImageRemove = (event) => {
    event.stopPropagation();
    setSelectedImagePreview(null);
  };

  const highestMatch = results.length > 0 ? results[0].percentage : 0;

  return (
    <Box m="20px">
      <Box display="flex" justifyContent="space-between" alignItems="center">
        <Header
          title="Search fact-checks"
          subtitle="Welcome! Search here for fact-checks using text or image queries"
        />
      </Box>
      <Box mb="20px" display="flex" alignItems="center">
        <FormLabel component="legend" sx={{ marginRight: 2, color: "black" }}>
          Search Type
        </FormLabel>
        <RadioGroup
          row
          aria-label="searchType"
          name="searchType"
          value={searchType}
          onChange={handleSearchTypeChange}
        >
          <FormControlLabel
            value="text"
            control={
              <Radio
                sx={{ color: "black", "&.Mui-checked": { color: "black" } }}
              />
            }
            label="Text"
            sx={{ color: "black" }}
          />
          <FormControlLabel
            value="image"
            control={
              <Radio
                sx={{ color: "black", "&.Mui-checked": { color: "black" } }}
              />
            }
            label="Image Upload"
            sx={{ color: "black" }}
          />
          <FormControlLabel
            value="link"
            control={
              <Radio
                sx={{ color: "black", "&.Mui-checked": { color: "black" } }}
              />
            }
            label="Image URL"
            sx={{ color: "black" }}
          />
        </RadioGroup>
      </Box>

      <Box display="flex" justifyContent="center" alignItems="center" mb="20px">
        {searchType === "text" && (
          <TextField
            inputRef={searchInputRef}
            variant="outlined"
            label="Search"
            size="medium"
            fullWidth
            InputLabelProps={{
              style: { color: "black" },
            }}
            sx={{
              "& .MuiOutlinedInput-root": {
                borderRadius: "80px", // Rounded corners
                "& fieldset": {
                  borderColor: "black",
                },
                "&:hover fieldset": {
                  borderColor: "black",
                },
                "&.Mui-focused fieldset": {
                  borderColor: "black",
                },
                "& input": {
                  color: "black", // Input text color
                },
              },
              "& .MuiInputLabel-root": {
                color: "black",
              },
            }}
            onKeyDown={handleSearchEnterKey}
          />
        )}

        {searchType === "link" && (
          <TextField
            value={imageUrl}
            onChange={(e) => setImageUrl(e.target.value)}
            variant="outlined"
            label="Image URL"
            size="medium"
            fullWidth
            InputLabelProps={{
              style: { color: "black" },
            }}
            sx={{
              "& .MuiOutlinedInput-root": {
                borderRadius: "80px", // Rounded corners
                "& fieldset": {
                  borderColor: "black",
                },
                "&:hover fieldset": {
                  borderColor: "black",
                },
                "&.Mui-focused fieldset": {
                  borderColor: "black",
                },
                "& input": {
                  color: "black", // Input text color
                },
              },
              "& .MuiInputLabel-root": {
                color: "black",
              },
            }}
            onKeyDown={handleSearchEnterKey}
          />
        )}

        {searchType === "image" && (
          <Box
            {...getRootProps()}
            InputLabelProps={{
              style: { color: "black" },
            }}
            sx={{
              display: "flex",
              alignItems: "center",
              justifyContent: "flex-start",
              width: "calc(100% - 15px - 10px)",
              minHeight: "50px",
              border: "1px solid #cccccc",
              borderRadius: "8px", // Rounded corners
              backgroundColor: "#fff",
              cursor: "pointer",
              paddingLeft: "10px",

              "& .MuiOutlinedInput-root": {
                borderRadius: "8px", // Rounded corners for input inside dropzone
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
                color: "#e5e5e5",
              },
            }}
          >
            <input {...getInputProps()} />
            {selectedImagePreview ? (
              <Box sx={{ position: "relative" }}>
                <img
                  src={selectedImagePreview}
                  alt="Selected"
                  style={{
                    width: "50px",
                    height: "50px",
                    objectFit: "cover",
                    marginRight: "10px",
                  }}
                />
                <IconButton
                  onClick={(event) => handleImageRemove(event)}
                  sx={{
                    position: "absolute",
                    top: 0,
                    right: 0,
                    color: "white",
                    backgroundColor: "black",
                    "&:hover": { backgroundColor: "black" },
                    zIndex: 2,
                  }}
                  size="small"
                >
                  <CloseIcon fontSize="small" />
                </IconButton>
              </Box>
            ) : (
              <Typography style={{ color: "black" }}>
                Drag 'n' drop an image here, or click to select one (jpeg/png)
              </Typography>
            )}
          </Box>
        )}

        <Button
          variant="contained"
          onClick={handleSearchButtonClick}
          sx={{
            backgroundColor: "#0b9933",
            color: colors.grey[100],
            borderRadius: "80px",
            marginLeft: "10px",
            fontSize: "14px",
            fontWeight: "bold",
            padding: "10px 20px",
            width: "100px",
          }}
        >
          Search
        </Button>
      </Box>
      {isLoading ? (
        <Box
          display="flex"
          justifyContent="center"
          alignItems="center"
          height="50vh"
          flexDirection="column"
        >
          <CircularProgress sx={{ color: colors.blueAccent[600] }} />
          <Typography variant="h6" sx={{ mt: 2 }}>
            Loading...
          </Typography>
        </Box>
      ) : (
        <>
          {isSearchInitiated && (
            <>
              {errorMessage ? (
                <Box display="flex" justifyContent="center" mt="20px">
                  <Typography color="error" variant="h2">
                    {errorMessage}
                  </Typography>
                </Box>
              ) : (
                <>
                  <Grid container spacing={2}>
                    {isSm ? (
                      <>
                        <Grid item xs={12}>
                          <Box
                            backgroundColor="#f4fff4"
                            p="30px"
                            mb="20px"
                            flexGrow={1}
                          >
                            {apiCallCompleted && (
                              <Box
                                display="flex"
                                flexDirection="column"
                                alignItems="center"
                                backgroundColor="#f4fff4"
                                sx={{ backgroundColor: "#f4fff4" }}
                              >
                                {results.length > 0 ? (
                                  <>
                                    <ProgressCircle
                                      size={isXs ? 100 : 125}
                                      progress={highestMatch / 100}
                                    />
                                    <Typography
                                      variant="h5"
                                      color={colors.greenAccent[100]}
                                      sx={{ mt: "15px" }}
                                    >
                                      This claim has up to {highestMatch}% match
                                      with debunked stories in our Database
                                    </Typography>
                                  </>
                                ) : (
                                  <Typography
                                    variant="h5"
                                    color={"black"}
                                    sx={{ mt: "15px" }}
                                  >
                                    This claim does not have any significant
                                    match with debunked stories in our DB.
                                  </Typography>
                                )}
                                <Typography
                                  sx={{
                                    fontSize: isXs ? "8px" : "10px",
                                    color: "black",
                                  }}
                                >
                                  Disclaimer: This section of the website is run
                                  by an AI tool which makes decisions based on
                                  deep learning mechanisms. The parties shall
                                  not bear any liability of the decisions made
                                  by the tool, but would ensure to take down any
                                  wrong decision as and when highlighted by any
                                  person or authority with sufficient proof and
                                  justification.
                                </Typography>
                              </Box>
                            )}
                          </Box>
                        </Grid>
                        <Grid item xs={12}>
                          <Box
                            backgroundColor={colors.primary[400]}
                            p="30px"
                            height="100%"
                            overflow="auto"
                          >
                            <Box
                              display="flex"
                              justifyContent="space-between"
                              alignItems="center"
                              borderBottom={`1px solid ${colors.primary[400]}`}
                              p="15px"
                              position="sticky"
                              top={0}
                              zIndex={10}
                              bgcolor={colors.primary[400]}
                            >
                              <Typography
                                color={colors.grey[100]}
                                variant="h5"
                                fontWeight="600"
                                sx={{ mt: "15px" }}
                              >
                                Top Matches
                              </Typography>
                              <Box>
                                <Button
                                  onClick={handlePrev}
                                  disabled={currentPage === 1}
                                  variant="contained"
                                  sx={{ mr: 1 }}
                                >
                                  Prev
                                </Button>
                                <Button
                                  onClick={handleNext}
                                  disabled={
                                    currentPage ===
                                    Math.ceil(results.length / itemsPerPage)
                                  }
                                  variant="contained"
                                  sx={{ ml: 1 }}
                                >
                                  Next
                                </Button>
                              </Box>
                            </Box>
                            {Array.isArray(currentItems) ? (
                              currentItems.map((result, index) => (
                                <Box
                                  key={index}
                                  display="flex"
                                  flexDirection={isXs ? "column" : "row"} // Stack image and text vertically on mobile
                                  alignItems="flex-start"
                                  borderBottom={`1px solid ${colors.primary[400]}`}
                                  p={isXs ? "0px" : "13px 3px"} // Less padding on mobile
                                >
                                  <ButtonBase
                                    onClick={() =>
                                      window.open(
                                        result.data.Story_URL,
                                        "_blank"
                                      )
                                    }
                                    sx={{
                                      marginRight: isXs ? "0" : "20px", // Remove side margin on mobile
                                      marginBottom: isXs ? "10px" : "0", // Add bottom margin on mobile
                                      borderRadius: "4px",
                                      overflow: "hidden",
                                      display: "flex",
                                      alignItems: "center",
                                      width: isXs ? "100%" : "auto", // Full width on mobile for better image display
                                      height: "auto", // Ensuring height is dynamic
                                    }}
                                  >
                                    <img
                                      src={result.data.img}
                                      alt="News"
                                      style={{
                                        width: isXs ? "100%" : "110px", // Full width on mobile
                                        height: isXs ? "auto" : "95px", // Auto height on mobile
                                        objectFit: "contain",
                                      }}
                                    />
                                  </ButtonBase>
                                  <div style={{ flex: 1, minWidth: "0" }}>
                                    <Typography
                                      color={colors.greenAccent[100]}
                                      variant="h5"
                                      fontWeight="600"
                                      style={{
                                        whiteSpace: "normal",
                                        overflow: "hidden",
                                      }} // Ensure text wraps and doesn't overflow
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
                                    <Typography
                                      color={colors.grey[100]}
                                      style={{ marginTop: "5px" }}
                                    >
                                      {result.data.Story_Date}
                                    </Typography>
                                  </div>
                                </Box>
                              ))
                            ) : (
                              <Typography color="error">
                                Error: Results are not available.
                              </Typography>
                            )}
                          </Box>
                        </Grid>
                        <Grid item xs={12}>
                          <Box
                            backgroundColor={colors.primary[400]}
                            p="30px"
                            flexGrow={1}
                          >
                            <Box
                              display="flex"
                              justifyContent="space-between"
                              alignItems="center"
                            >
                              <Typography
                                variant="h5"
                                fontWeight="600"
                                color={colors.grey[100]}
                              >
                                Timeline
                              </Typography>
                            </Box>
                            <Box height="250px">
                              <LineChart data={chartData} isDashboard={true} />
                            </Box>
                          </Box>
                        </Grid>
                      </>
                    ) : (
                      <>
                        <Grid item xs={12} md={5} container direction="column">
                          <Box
                            backgroundColor="#f4fff4"
                            p="30px"
                            mb="20px"
                            flexGrow={1}
                          >
                            {apiCallCompleted && (
                              <Box
                                display="flex"
                                flexDirection="column"
                                alignItems="center"
                                backgroundColor="#f4fff4"
                              >
                                {results.length > 0 ? (
                                  <>
                                    <ProgressCircle
                                      size={isXs ? 100 : 125}
                                      progress={highestMatch / 100}
                                    />
                                    <Typography
                                      variant="h5"
                                      color={colors.greenAccent[100]}
                                      sx={{ mt: "15px" }}
                                    >
                                      This claim has up to {highestMatch}% match
                                      with debunked stories in our Database
                                    </Typography>
                                  </>
                                ) : (
                                  <Typography
                                    variant="h5"
                                    color={colors.greenAccent[100]}
                                    sx={{ mt: "15px" }}
                                  >
                                    This claim does not have any significant
                                    match with debunked stories in our DB.
                                  </Typography>
                                )}
                                <Typography
                                  sx={{
                                    fontSize: isXs ? "8px" : "10px",
                                    color: "black",
                                  }}
                                >
                                  Disclaimer: This section of the website is run
                                  by an AI tool which makes decisions based on
                                  deep learning mechanisms. The parties shall
                                  not bear any liability of the decisions made
                                  by the tool, but would ensure to take down any
                                  wrong decision as and when highlighted by any
                                  person or authority with sufficient proof and
                                  justification.
                                </Typography>
                              </Box>
                            )}
                          </Box>
                          <Box
                            p="30px"
                            flexGrow={1}
                            sx={{ border: "1px solid #e5e5e5" }} // Added border color
                          >
                            <Box
                              display="flex"
                              justifyContent="space-between"
                              alignItems="center"
                            >
                              <Typography
                                variant="h5"
                                fontWeight="600"
                                color={colors.grey[100]}
                              >
                                Timeline
                              </Typography>
                            </Box>
                            <Box height="250px">
                              <LineChart data={chartData} isDashboard={true} />
                            </Box>
                          </Box>
                        </Grid>
                        <Grid item xs={12} md={7}>
                          <Box p="30px" height="100%" overflow="auto">
                            <Box
                              display="flex"
                              justifyContent="space-between"
                              alignItems="center"
                              borderBottom={`1px solid ${colors.primary[400]}`}
                              p="15px"
                              position="sticky"
                              top={0}
                              zIndex={10}
                            >
                              <Typography
                                color={colors.grey[100]}
                                variant="h5"
                                fontWeight="600"
                                sx={{ mt: "15px" }}
                              >
                                Top Matches
                              </Typography>
                              <Box>
                                <Button
                                  onClick={handlePrev}
                                  disabled={currentPage === 1}
                                  variant="contained"
                                  sx={{ mr: 1 }}
                                >
                                  Prev
                                </Button>
                                <Button
                                  onClick={handleNext}
                                  disabled={
                                    currentPage ===
                                    Math.ceil(results.length / itemsPerPage)
                                  }
                                  variant="contained"
                                  sx={{ ml: 1 }}
                                >
                                  Next
                                </Button>
                              </Box>
                            </Box>
                            {Array.isArray(currentItems) ? (
                              currentItems.map((result, index) => (
                                <Box
                                  key={index}
                                  display="flex"
                                  flexDirection="row"
                                  alignItems="flex-start"
                                  borderBottom={`1px solid ${colors.primary[400]}`}
                                  p=" 13px 35px"
                                >
                                  <ButtonBase
                                    onClick={() =>
                                      window.open(
                                        result.data.Story_URL,
                                        "_blank"
                                      )
                                    }
                                    sx={{
                                      marginRight: "20px",
                                      borderRadius: "4px",
                                      overflow: "hidden",
                                    }}
                                  >
                                    <img
                                      src={result.data.img}
                                      alt="News"
                                      width="110px"
                                      height="95px"
                                      style={{ marginRight: "20px" }}
                                    />
                                  </ButtonBase>
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
                                  </div>
                                  {errorMessage && (
                                    <Typography color="error" sx={{ p: 2 }}>
                                      {errorMessage}
                                    </Typography>
                                  )}
                                </Box>
                              ))
                            ) : (
                              <Typography color="error">
                                Error: Results are not available.
                              </Typography>
                            )}
                          </Box>
                        </Grid>
                      </>
                    )}
                  </Grid>
                </>
              )}
            </>
          )}
        </>
      )}
    </Box>
  );
};

export default Dashboard;
