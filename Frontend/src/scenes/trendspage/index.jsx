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

const Trendspage = () => {
  const [resultsColumn1, setResultsColumn1] = useState([]);
  const [expandedQuery, setExpandedQuery] = useState(null);
  const [isLoadingColumn1, setIsLoadingColumn1] = useState(false);
  const [resultsColumn2, setResultsColumn2] = useState([]);
  const [isLoadingColumn2, setIsLoadingColumn2] = useState(false);
  const [currentPageColumn1, setCurrentPageColumn1] = useState(1);
  const [currentPageColumn2, setCurrentPageColumn2] = useState(1);
  const [errorColumn1, setErrorColumn1] = useState(null);
  const [errorColumn2, setErrorColumn2] = useState(null);
  const [showAllResultsColumn1, setShowAllResultsColumn1] = useState(false);
  const itemsPerPageColumn2 = 7;

  const theme = useTheme();
  const colors = tokens(theme.palette.mode);
  const isMobile = useMediaQuery(theme.breakpoints.down("sm")); // Detect mobile mode
  // const indexOfLastItemColumn1 = currentPageColumn1 * itemsPerPageColumn1;
  // const indexOfFirstItemColumn1 = indexOfLastItemColumn1 - itemsPerPageColumn1;
  // const currentItemsColumn1 = resultsColumn1.slice(
  //   indexOfFirstItemColumn1,
  //   indexOfLastItemColumn1
  // );

  const indexOfLastItemColumn2 = currentPageColumn2 * itemsPerPageColumn2;
  const indexOfFirstItemColumn2 = indexOfLastItemColumn2 - itemsPerPageColumn2;
  const currentItemsColumn2 = resultsColumn2.slice(
    indexOfFirstItemColumn2,
    indexOfLastItemColumn2
  );

  const handleNextColumn1 = () => {
    setCurrentPageColumn1(currentPageColumn1 + 1);
  };

  const handlePrevColumn1 = () => {
    setCurrentPageColumn1(currentPageColumn1 - 1);
  };

  const handleNextColumn2 = () => {
    setCurrentPageColumn2(currentPageColumn2 + 1);
  };

  const handlePrevColumn2 = () => {
    setCurrentPageColumn2(currentPageColumn2 - 1);
  };
  useEffect(() => {
    fetchTopTrends();
    fetchResultsForColumn2();
  }, []);

  const fetchTopTrends = () => {
    setIsLoadingColumn1(true);
    // fetch("https://factcheckerbtp.vishvasnews.com/api/top-trends")
    fetch("/api/top-trends")
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

    // fetch("https://factcheckerbtp.vishvasnews.com/api/stories-by-date", {
    fetch("/api/stories-by-date", {
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

  const renderResultsColumn1 = (results) => {
    const itemsToShow = isMobile && !showAllResultsColumn1 ? 4 : results.length;

    return (
      <>
        {results.slice(0, itemsToShow).map((result, index) => (
          <Box key={index} mb="20px">
            {result.results.map((item, subIndex) => (
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
                    width={isMobile ? "250px" : "150px"} // Conditional width
                    height="95px" // Fixed height
                    style={{ marginRight: "20px" }}
                  />
                </ButtonBase>
                <div>
                  <Typography variant="h5" color={"#00ab05"}>
                    {result.query}
                  </Typography>
                  <Typography
                    color={colors.greenAccent[100]}
                    variant="h6"
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
        {isMobile && !showAllResultsColumn1 && results.length > 4 && (
          <Box display="flex" justifyContent="center" mt="20px">
            <Button
              onClick={() => setShowAllResultsColumn1(true)}
              variant="contained"
            >
              Load More
            </Button>
          </Box>
        )}
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
            sx={{ mr: 1 }}
          >
            Prev
          </Button>
          <Button
            onClick={handleNext}
            disabled={currentPage === Math.ceil(results.length / itemsPerPage)}
            variant="contained"
            sx={{ ml: 1 }}
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
              Recycled dis/misinformation is often deployed by bad actors to
              create confusion and mislead recipients.
              <br /> This section shows you already debunked dis/misinformation
              based on:
              <br /> <b>Current trends </b>– Fact-checks by our team based on
              what is trending on the web.
              <br /> <b>Historical trends</b> – Fact-checks from the past years,
              on the same date and week +/- three days.
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
              Based on Current Trends
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
              renderResultsColumn1(resultsColumn1)
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
              Based on Historical Trends
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
