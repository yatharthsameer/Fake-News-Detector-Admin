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
import { useTranslation } from "react-i18next";

const Dashboard = () => {
  const { t } = useTranslation(); // Adding the translation hook
  const theme = useTheme();
  const colors = tokens(theme.palette.mode);
  const isXs = useMediaQuery(theme.breakpoints.down("xs"));
  const isSm = useMediaQuery(theme.breakpoints.down("sm"));
  const isMd = useMediaQuery(theme.breakpoints.down("md"));
  const isMobile = useMediaQuery(theme.breakpoints.down("sm")); // Detect mobile mode

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
      id: "No. of fact checks",
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
      const MAX_FILE_SIZE = 7 * 1000 * 1000;
      if (selectedImageFile.size > MAX_FILE_SIZE) {
        setIsLoading(false);
        setApiCallCompleted(true);
        setErrorMessage("File size is too large. Maximum allowed size is 5MB.");
        return;
      }

      const formData = new FormData();
      formData.append("file", selectedImageFile);

      fetch("/api/upload", {
        method: "POST",
        body: formData,
      })
        .then((response) => {
          setIsLoading(false);
          setApiCallCompleted(true);
          if (!response.ok) {
            return response.json().then((data) => {
              setErrorMessage(data.error || "Unknown error occurred");
              return null;
            });
          }
          return response.json();
        })
        .then((data) => {
          if (data) {
            setResults(data);
            setChartData(processChartData(data));
            setErrorMessage("");
          }
        })
        .catch((error) => {
          setIsLoading(false);
          setApiCallCompleted(true);
          setErrorMessage(
            "The server encountered some issue, please click search again."
          );
        });
    } else if (searchType === "link" && imageUrl.trim()) {
      const imgURLQ = imageUrl.trim();

      fetch("/api/uploadImageURL", {
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
          if (data.error) {
            setErrorMessage(data.error);
            setApiCallCompleted(true);
          } else {
            setResults(data);
            setChartData(processChartData(data));
            setApiCallCompleted(true);
            setErrorMessage("");
          }
        })
        .catch((error) => {
          setIsLoading(false);
          setApiCallCompleted(true);
          setErrorMessage(
            "The server encountered some issue, please click search again."
          );
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
    <Box mt="40px">
      <Box display="flex" justifyContent="space-between" alignItems="center">
        <Header
          title={t("message_check")} // Using key from en.json
          subtitle={
            <>
              {t("welcome_message_check")}
              <br /> <br />
              {t("verify_authenticity")}
              <br />
              {t("use_search_bar")}
              <br /> <br />
              {t("system_info")}
              <br />
              {t("important_topics")}
            </>
          }
        />
      </Box>

      <Box mb="20px" display="flex" alignItems="center">
        <FormLabel component="legend" sx={{ marginRight: 2, color: "black" }}>
          {t("search_type")}
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
            label={t("text")} // Using key for Text label
            sx={{ color: "black" }}
          />
          <FormControlLabel
            value="image"
            control={
              <Radio
                sx={{ color: "black", "&.Mui-checked": { color: "black" } }}
              />
            }
            label={t("image_upload")} // Using key for Image Upload label
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
                borderRadius: "80px",
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
                  color: "black",
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
            label={t("image_url")}
            size="medium"
            fullWidth
            InputLabelProps={{
              style: { color: "black" },
            }}
            sx={{
              "& .MuiOutlinedInput-root": {
                borderRadius: "80px",
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
                  color: "black",
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
              borderRadius: "8px",
              backgroundColor: "#fff",
              cursor: "pointer",
              paddingLeft: "10px",

              "& .MuiOutlinedInput-root": {
                borderRadius: "8px",
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
                  color: "black",
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
                {/* {t("drag_drop_image")} */}
                {t("drag_drop_image")}
              </Typography>
            )}
          </Box>
        )}

        <Button
          variant="contained"
          onClick={handleSearchButtonClick}
          sx={{
            backgroundColor: "#0b9933",
            color: "white",

            borderRadius: "80px",
            marginLeft: "10px",
            fontSize: "14px",
            fontWeight: "bold",
            padding: "10px 20px",
            width: "100px",
          }}
        >
          {t("search")}
        </Button>
      </Box>

      {isSearchInitiated && apiCallCompleted && (
        <Box mt={3} mb={3}>
          <Typography variant="body1" sx={{ color: "black" }}>
            {t("information")}
          </Typography>
        </Box>
      )}

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
            {t("loading")}{" "}
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
                                    {t("no_match_message")}
                                  </Typography>
                                )}
                                <Typography
                                  sx={{
                                    fontSize: isXs ? "8px" : "10px",
                                    color: "black",
                                  }}
                                >
                                  {t("disclaimer")}
                                </Typography>
                              </Box>
                            )}
                          </Box>
                        </Grid>
                        <Grid item xs={12}>
                          <Box
                            backgroundColor={colors.primary[400]}
                            // p="30px"
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
                                {t("top_matches")}
                              </Typography>
                            </Box>
                            {Array.isArray(currentItems) ? (
                              currentItems.map((result, index) => (
                                <Box
                                  key={index}
                                  display="flex"
                                  flexDirection={isXs ? "column" : "row"}
                                  alignItems="flex-start"
                                  borderBottom={`1px solid ${colors.primary[400]}`}
                                  p={isXs ? "0px" : "13px 3px"}
                                >
                                  <ButtonBase
                                    onClick={() =>
                                      window.open(
                                        result.data.Story_URL,
                                        "_blank"
                                      )
                                    }
                                    sx={{
                                      marginRight: isXs ? "0" : "20px",
                                      marginBottom: isXs ? "10px" : "0",
                                      borderRadius: "4px",
                                      overflow: "hidden",
                                      display: "flex",
                                      alignItems: "center",
                                      width: isXs ? "100%" : "auto",
                                      height: "auto",
                                    }}
                                  >
                                    <img
                                      src={
                                        result.data.img &&
                                        result.data.img.length > 0
                                          ? result.data.img[0]
                                          : ""
                                      }
                                      alt="News"
                                      width={isMobile ? "140px" : "150px"} // Conditional width
                                      height="95px"
                                      style={{ marginRight: "20px" }}
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
                                      }}
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
                                {t("error_results_not_available")}{" "}
                              </Typography>
                            )}
                            <Box display="flex" justifyContent="center" mt={2}>
                              <Button
                                onClick={handlePrev}
                                disabled={currentPage === 1}
                                variant="contained"
                                sx={{
                                  mr: 1,
                                  backgroundColor: "#0b9933",
                                  color: "white",
                                  "&:hover": { backgroundColor: "#9E9E9E" },
                                }}
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
                                sx={{
                                  mr: 1,
                                  backgroundColor: "#0b9933",
                                  color: "white",
                                  "&:hover": { backgroundColor: "#9E9E9E" },
                                }}
                              >
                                Next
                              </Button>
                            </Box>
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
                                {t("timeline")}{" "}
                              </Typography>
                            </Box>
                            <Box height="250px">
                              <LineChart data={chartData} isDashboard={true} />
                            </Box>
                            <Typography
                              variant="body2"
                              color="black"
                              align="center"
                              mt={2}
                            >
                              {t("timeline_description")}{" "}
                              {/* i18n key for timeline description */}
                            </Typography>
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
                                      {t("claim_match_message", {
                                        highestMatch,
                                      })}
                                      {/* i18n key for match percentage */}
                                    </Typography>
                                  </>
                                ) : (
                                  <Typography
                                    variant="h5"
                                    color={colors.greenAccent[100]}
                                    sx={{ mt: "15px" }}
                                  >
                                    {t("no_match_message")}
                                  </Typography>
                                )}
                                <Typography
                                  sx={{
                                    fontSize: isXs ? "8px" : "10px",
                                    color: "black",
                                  }}
                                >
                                  {t("disclaimer")}
                                </Typography>
                              </Box>
                            )}
                          </Box>
                          <Box
                            p="30px"
                            flexGrow={1}
                            sx={{ border: "1px solid #e5e5e5" }}
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
                                {t("timeline")}{" "}
                              </Typography>
                            </Box>
                            <Box height="250px">
                              <LineChart data={chartData} isDashboard={true} />
                            </Box>
                            <Typography
                              variant="body2"
                              color="black"
                              align="center"
                              mt={2}
                            >
                              {t("timeline_description")}
                            </Typography>
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
                                {t("top_matches")}
                              </Typography>
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
                                      src={
                                        result.data.img &&
                                        result.data.img.length > 0
                                          ? result.data.img[0]
                                          : ""
                                      }
                                      alt="News"
                                      width={isMobile ? "250px" : "150px"} // Conditional width
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
                                {t("error_results_not_available")}{" "}
                                {/* i18n key for error message */}
                              </Typography>
                            )}
                            <Box display="flex" justifyContent="center" mt={2}>
                              <Button
                                onClick={handlePrev}
                                disabled={currentPage === 1}
                                variant="contained"
                                sx={{
                                  mr: 1,
                                  backgroundColor: "#0b9933",
                                  color: "white",
                                  "&:hover": { backgroundColor: "#9E9E9E" },
                                }}
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
                                sx={{
                                  mr: 1,
                                  backgroundColor: "#0b9933",
                                  color: "white",
                                  "&:hover": { backgroundColor: "#9E9E9E" },
                                }}
                              >
                                Next
                              </Button>
                            </Box>
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
