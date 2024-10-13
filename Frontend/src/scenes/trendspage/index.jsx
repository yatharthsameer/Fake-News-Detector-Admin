import React, { useState, useEffect } from "react";
import {
  Box,
  Button,
  Typography,
  CircularProgress,
  ButtonBase,
  useTheme,
  Grid,
  useMediaQuery,
} from "@mui/material";
import { tokens } from "../../theme";
import Header from "../../components/Header";
import { useTranslation } from "react-i18next"; // Translation hook

const Trendspage = () => {
  const [resultsColumn1, setResultsColumn1] = useState([]);
  const [isLoadingColumn1, setIsLoadingColumn1] = useState(false);
  const [currentPageColumn1, setCurrentPageColumn1] = useState(1); // Use this state
  const [errorColumn1, setErrorColumn1] = useState(null);
  const [resultsColumn2, setResultsColumn2] = useState([]);
  const [isLoadingColumn2, setIsLoadingColumn2] = useState(false);
  const [currentPageColumn2, setCurrentPageColumn2] = useState(1); // Use this state
  const [errorColumn2, setErrorColumn2] = useState(null);
  const itemsPerPageColumn1 = 3; // Show 5 results per page in column 1
  const itemsPerPageColumn2 = 7;
  const { t } = useTranslation(); // Translation hook

  const theme = useTheme();
  const colors = tokens(theme.palette.mode);
  const isMobile = useMediaQuery(theme.breakpoints.down("sm")); // Detect mobile mode

  useEffect(() => {
    fetchTopTrends();
    fetchResultsForColumn2();
  }, []);

  const fetchTopTrends = () => {
    setIsLoadingColumn1(true);
    fetch("https://factcheckerbtp.vishvasnews.com/api/top-trends")
      .then((response) => response.json())
      .then((data) => {
        const flattenedData = [];
        data.forEach((trend) => {
          Object.entries(trend).forEach(([query, results]) => {
            flattenedData.push({ query, results });
          });
        });
        setResultsColumn1(flattenedData);
        setIsLoadingColumn1(false);
      })
      .catch((error) => {
        console.error("Error fetching top trends:", error);
        setIsLoadingColumn1(false);
        setResultsColumn1([]);
        setErrorColumn1("Error fetching top trends.");
      });
  };

  const fetchResultsForColumn2 = () => {
    setIsLoadingColumn2(true);
    const currentDate = new Date();
    const formattedDate = `${currentDate.getDate()} ${currentDate.toLocaleString(
      "default",
      { month: "short" }
    )} ${currentDate.getFullYear()}`;

    fetch("https://factcheckerbtp.vishvasnews.com/api/stories-by-date", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        charset: "utf-8",
      },
      body: JSON.stringify({ date: formattedDate }),
    })
      .then((response) => response.json())
      .then((data) => {
        setResultsColumn2(data);
        setIsLoadingColumn2(false);
      })
      .catch((error) => {
        console.error("Error fetching data for column 2:", error);
        setIsLoadingColumn2(false);
        setResultsColumn2([]);
        setErrorColumn2("Error fetching data for the selected date.");
      });
  };

  // Define the functions for navigating pages in Column 1
  const handleNextColumn1 = () => {
    setCurrentPageColumn1((prevPage) => prevPage + 1);
  };

  const handlePrevColumn1 = () => {
    setCurrentPageColumn1((prevPage) =>
      prevPage > 1 ? prevPage - 1 : prevPage
    );
  };

  // Define the functions for navigating pages in Column 2
  const handleNextColumn2 = () => {
    setCurrentPageColumn2((prevPage) => prevPage + 1);
  };

  const handlePrevColumn2 = () => {
    setCurrentPageColumn2((prevPage) =>
      prevPage > 1 ? prevPage - 1 : prevPage
    );
  };
  const renderResultsColumn1 = (
    results,
    currentPage,
    handlePrev,
    handleNext,
    itemsPerPage
  ) => {
    const indexOfLastItem = currentPage * itemsPerPage;
    const indexOfFirstItem = indexOfLastItem - itemsPerPage;
    const currentItems = results.slice(indexOfFirstItem, indexOfLastItem);

    return (
      <>
        {currentItems.map((result, index) => (
          <Box key={index} mb="20px">
            {/* Trend Title */}
            <Typography variant="h5" color={"#00ab05"} mb="10px">
              {result.query}
            </Typography>

            {/* Display up to 2 news objects */}
            {result.results.slice(0, 2).map((item, subIndex) => (
              <Box
                key={subIndex}
                display="flex"
                flexDirection="row"
                alignItems="flex-start"
                borderBottom={`1px solid ${colors.primary[400]}`}
                p="10px 0"
              >
                <ButtonBase
                  onClick={() => window.open(item.data.Story_URL, "_blank")}
                  sx={{
                    marginRight: "20px",
                    borderRadius: "4px",
                    overflow: "hidden",
                  }}
                >
                  <img
                    src={
                      item.data.img && item.data.img.length > 0
                        ? item.data.img[0]
                        : ""
                    }
                    alt="News"
                    width={isMobile ? "250px" : "150px"}
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
                      href={item.data.Story_URL}
                      target="_blank"
                      rel="noopener noreferrer"
                      style={{
                        color: colors.greenAccent[100],
                        textDecoration: "none",
                      }}
                    >
                      {item.data.Headline}
                    </a>
                  </Typography>
                  <Typography color={colors.grey[100]}>
                    {item.data.Story_Date}
                  </Typography>
                </div>
              </Box>
            ))}
          </Box>
        ))}
        <Box display="flex" justifyContent="center" mt="20px">
          <Button
            onClick={handlePrev}
            disabled={currentPage === 1}
            variant="contained"
            sx={{
              mr: 1,
              mb: 5,
              backgroundColor: "#0b9933",
              color: "white",
              "&:hover": { backgroundColor: "#9E9E9E" },
            }}
          >
            Prev
          </Button>
          <Button
            onClick={handleNext}
            disabled={currentPage === Math.ceil(results.length / itemsPerPage)}
            variant="contained"
            sx={{
              mr: 1,
              mb: 5,
              backgroundColor: "#0b9933",
              color: "white",
              "&:hover": { backgroundColor: "#9E9E9E" },
            }}
          >
            Next
          </Button>
        </Box>
      </>
    );
  };

  const renderResultsColumn2 = (
    results,
    currentPage,
    handlePrev,
    handleNext,
    itemsPerPage
  ) => {
    const indexOfLastItem = currentPage * itemsPerPage;
    const indexOfFirstItem = indexOfLastItem - itemsPerPage;
    const currentItems = results.slice(indexOfFirstItem, indexOfLastItem);

    return (
      <>
        {currentItems.map((result, index) => (
          <Box
            key={index}
            display="flex"
            flexDirection="row"
            alignItems="flex-start"
            borderBottom={`1px solid ${colors.primary[400]}`}
            p="10px 0"
          >
            <ButtonBase
              onClick={() => window.open(result.data.Story_URL, "_blank")}
              sx={{
                marginRight: "20px",
                borderRadius: "4px",
                overflow: "hidden",
              }}
            >
              <img
                src={
                  result.data.img && result.data.img.length > 0
                    ? result.data.img[0]
                    : ""
                }
                alt="News"
                width={isMobile ? "250px" : "150px"} // Conditional width
                height="95px" // Fixed height
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
          </Box>
        ))}
        <Box display="flex" justifyContent="center" mt="20px">
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
            disabled={currentPage === Math.ceil(results.length / itemsPerPage)}
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
      </>
    );
  };

  return (
    <Box mt="40px">
      <Box display="flex" justifyContent="space-between" alignItems="center">
        <Header
          title="Trends based misinformation"
          subtitle={
            <>
              {t("recycled_misinformation")}
              <br /> {t("debunked_section")}
              <br /> <b>{t("current_trends")}</b>
              <br /> <b>{t("historical_trends")}</b>
            </>
          }
        />
      </Box>
      <Grid container spacing={2}>
        <Grid item xs={12} md={6}>
          <Box>
            <Typography
              variant="h5"
              color={colors.grey[100]}
              mb="10px"
              fontWeight="bold"
            >
              {t("based_on_current_trends")}{" "}
            </Typography>
            {isLoadingColumn1 ? (
              <Box
                display="flex"
                justifyContent="center"
                alignItems="center"
                height="50vh"
              >
                <CircularProgress sx={{ color: colors.blueAccent[600] }} />
                <Typography variant="h6" sx={{ mt: 2 }}>
                  Loading...
                </Typography>
              </Box>
            ) : errorColumn1 ? (
              <Typography color="error" variant="h6">
                {errorColumn1}
              </Typography>
            ) : (
              renderResultsColumn1(
                resultsColumn1,
                currentPageColumn1,
                handlePrevColumn1,
                handleNextColumn1,
                itemsPerPageColumn1
              )
            )}
          </Box>
        </Grid>
        <Grid item xs={12} md={6}>
          <Box>
            <Typography
              variant="h5"
              color={colors.grey[100]}
              mb="10px"
              fontWeight="bold"
            >
              {t("based_on_historical_trends")}{" "}
            </Typography>

            {isLoadingColumn2 ? (
              <Box
                display="flex"
                justifyContent="center"
                alignItems="center"
                height="50vh"
              >
                <CircularProgress sx={{ color: colors.blueAccent[600] }} />
                <Typography variant="h6" sx={{ mt: 2 }}>
                  Loading...
                </Typography>
              </Box>
            ) : errorColumn2 ? (
              <Typography color="error" variant="h6">
                {errorColumn2}
              </Typography>
            ) : (
              renderResultsColumn2(
                resultsColumn2,
                currentPageColumn2,
                handlePrevColumn2,
                handleNextColumn2,
                itemsPerPageColumn2
              )
            )}
          </Box>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Trendspage;
