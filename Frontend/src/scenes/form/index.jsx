import React, { useContext, useState } from "react";
import {
  Box,
  Button,
  TextField,
  Typography,
  IconButton,
  CircularProgress,
  useTheme,
} from "@mui/material";

import { Formik, FieldArray } from "formik";
import * as yup from "yup";
import { useNavigate } from "react-router-dom";
import { AuthContext } from "../../context/AuthContext";
import { useDropzone } from "react-dropzone";
import CloseIcon from "@mui/icons-material/Close";
import { ToggleButton, ToggleButtonGroup } from "@mui/material";
import { tokens } from "../../theme";

const storyDateValidation = yup
  .string()
  .matches(
    /^(?:[1-9]|[12][0-9]|3[01])(st|nd|rd|th) (Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) \d{4}$/,
    "Story Date must be in the format '24th Jul 2024' or '8th Oct 2020'"
  );

const validationSchema = yup.object().shape({
  Story_Date: storyDateValidation.required("Story date is required"),
  Story_URL: yup
    .string()
    .url("Enter a valid URL")
    .required("Story URL is required"),
  Headline: yup.string().required("Headline is required"),
  "What_(Claim)": yup.string().required("Claim is required"),
  img: yup.array().of(yup.string().url("Enter a valid image URL")),
  About_Person: yup.string().notRequired(),
  About_Subject: yup.string().required("Subject is required"),
});

const initialValues = {
  Story_Date: "",
  Story_URL: "",
  Headline: "",
  "What_(Claim)": "",
  tags: "",
  img: [""], // Initialize with one empty string for the first image URL
  About_Person: "",
  About_Subject: "",
};

const Form = () => {
  const { isAuthenticated, setIsAuthenticated } = useContext(AuthContext);
  const [file, setFile] = useState(null);
  const [message, setMessage] = useState("");
  const [isError, setIsError] = useState(false);
  const navigate = useNavigate();
  const [view, setView] = useState("csv");
  const [isLoading, setIsLoading] = useState(false);

  const onDrop = (acceptedFiles) => {
    setFile(acceptedFiles[0]);
  };

  const removeFile = () => {
    setFile(null);
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: "text/csv",
    noClick: file != null,
    noKeyboard: file != null,
  });

  const csvInstructions =
    "Ensure your CSV file has the columns in this order: Story Date, Story URL, Headline, What (Claim), About Subject, About Person, Featured Image, Tags.";

  const handleCSVSubmit = async () => {
    setIsLoading(true);
    setMessage("");
    if (!file) {
      setMessage("No file selected");
      setIsError(true);
      setIsLoading(false);
      return;
    }
    const formData = new FormData();
    formData.append("file", file);
    try {
      const response = await fetch("/api/appendDataCSV", {
        method: "POST",
        body: formData,
      });

      const result = await response.json();

      if (!response.ok) {
        let errorMessage = "Failed to upload CSV.";
        if (result.error) {
          errorMessage =
            result.error +
            (result.missing_columns
              ? " Missing columns: " + result.missing_columns.join(", ") + "."
              : "");
        }
        if (result.error_details && result.error_details.length > 0) {
          const detailedErrors = result.error_details
            .map((detail) => `Row ${detail.row}: ${detail.error}`)
            .join("; ");
          errorMessage += " Details: " + detailedErrors;
        }
        setMessage(errorMessage);
        setIsError(true);
      } else {
        setMessage(result.message);
        setIsError(false);
        setFile(null);
      }
      setIsLoading(false);
    } catch (error) {
      setIsLoading(false);
      console.error("An error occurred during CSV submission:", error);
      setMessage(`CSV submission error: ${error.message}`);
      setIsError(true);
    }
  };

  const handleFormSubmit = async (values) => {
    setIsLoading(true);
    setMessage("");
    try {
      const response = await fetch("/api/appendDataIndividual", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          charset: "utf-8",
        },
        body: JSON.stringify(values),
      });
      const result = await response.json();
      if (!response.ok) {
        setMessage(result.error || "Failed to submit data");
        setIsError(true);
      } else {
        setMessage(result.message || "Data submitted successfully");
        setIsError(false);
      }
    } catch (error) {
      console.error("An error occurred during form submission:", error);
      setMessage(`Form submission error: ${error.message}`);
      setIsError(true);
    }
    setIsLoading(false);
  };

  const theme = useTheme();
  const colors = tokens(theme.palette.mode);

  const handleLogout = async () => {
    console.log("Logging out");
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
      alert("Logged out successfully");
      navigate("/login");
    }
  };

  return (
    <Box m="20px">
      <Typography
        variant="h4"
        component="h2"
        sx={{ color: "black" }}
        align="center"
        gutterBottom
      >
        Add Fact Check(s)
      </Typography>

      <ToggleButtonGroup
        color="primary"
        value={view}
        exclusive
        onChange={(event, newView) => {
          if (newView !== null) {
            setView(newView);
          }
        }}
        aria-label="View"
        style={{
          marginBottom: 20,
          backgroundColor: "#282c34",
          borderRadius: 5,
        }}
        fullWidth
      >
        <ToggleButton
          value="csv"
          aria-label="CSV Upload"
          style={{
            width: "50%",
            borderRadius: 5,
            borderRight: "1px solid white",
            backgroundColor: view === "csv" ? "#4caf50" : undefined,
            color: view === "csv" ? "white" : "rgba(255, 255, 255, 0.7)",
          }}
        >
          CSV Upload
        </ToggleButton>
        <ToggleButton
          value="form"
          aria-label="Form Input"
          style={{
            width: "50%",
            borderRadius: 5,
            backgroundColor: view === "form" ? "#4caf50" : undefined,
            color: view === "form" ? "white" : "rgba(255, 255, 255, 0.7)",
          }}
        >
          Form Input
        </ToggleButton>
      </ToggleButtonGroup>

      {view === "csv" ? (
        <div
          {...getRootProps()}
          style={{
            position: "relative",
            width: "100%",
            height: "50px",
            border: "2px dashed gray",
          }}
        >
          <input {...getInputProps()} />
          {!file && (
            <Typography sx={{ p: 2, textAlign: "center", color: "black" }}>
              {isDragActive
                ? "Drop the file here..."
                : "Drag 'n' drop your CSV file here, or click to select files"}
            </Typography>
          )}
          {file && (
            <Box
              sx={{
                position: "relative",
                display: "flex",
                alignItems: "center",
                p: 1,
                bgcolor: "background.paper",
                border: "1px solid black",
                borderRadius: "4px",
              }}
            >
              <Typography noWrap sx={{ mr: 1 }}>
                {file.name}
              </Typography>
              <IconButton onClick={removeFile} size="small">
                <CloseIcon />
              </IconButton>
            </Box>
          )}
          <Typography variant="body1" sx={{ mb: 2, color: "black" }}>
            {csvInstructions}
          </Typography>
          {isLoading && (
            <Box
              display="flex"
              justifyContent="center"
              alignItems="center"
              height="50vh"
              flexDirection="column"
            >
              <CircularProgress sx={{ color: "black" }} />
              <Typography variant="h6" sx={{ mt: 2 }}>
                Adding entries to the database, please wait...
              </Typography>
            </Box>
          )}
          <Box mt={4}>
            <br />
            <br />
            <Typography
              variant="h6"
              sx={{
                color: "black",
              }}
            >
              Sample CSV Format:
            </Typography>
            <table style={{ width: "100%", borderCollapse: "collapse" }}>
              <thead>
                <tr>
                  <th
                    style={{
                      border: "1px solid black",
                      padding: "8px",
                      color: "black",
                    }}
                  >
                    Story Date
                  </th>
                  <th
                    style={{
                      border: "1px solid black",
                      padding: "8px",
                      color: "black",
                    }}
                  >
                    Story URL
                  </th>
                  <th
                    style={{
                      border: "1px solid black",
                      padding: "8px",
                      color: "black",
                    }}
                  >
                    Headline
                  </th>
                  <th
                    style={{
                      border: "1px solid black",
                      padding: "8px",
                      color: "black",
                    }}
                  >
                    What (Claim)
                  </th>
                  <th
                    style={{
                      border: "1px solid black",
                      padding: "8px",
                      color: "black",
                    }}
                  >
                    About Subject
                  </th>
                  <th
                    style={{
                      border: "1px solid black",
                      padding: "8px",
                      color: "black",
                    }}
                  >
                    About Person
                  </th>
                  <th
                    style={{
                      border: "1px solid black",
                      padding: "8px",
                      color: "black",
                    }}
                  >
                    Tags
                  </th>
                  <th
                    style={{
                      border: "1px solid black",
                      padding: "8px",
                      color: "black",
                    }}
                  >
                    Featured Image 1
                  </th>
                  <th
                    style={{
                      border: "1px solid black",
                      padding: "8px",
                      color: "black",
                    }}
                  >
                    Featured Image 2
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td
                    style={{
                      border: "1px solid black",
                      padding: "8px",
                      color: "black",
                    }}
                  >
                    24th Jul 2024
                  </td>
                  <td
                    style={{
                      border: "1px solid black",
                      padding: "8px",
                      color: "black",
                    }}
                  >
                    http://example.com
                  </td>
                  <td
                    style={{
                      border: "1px solid black",
                      padding: "8px",
                      color: "black",
                    }}
                  >
                    Sample Headline
                  </td>
                  <td
                    style={{
                      border: "1px solid black",
                      padding: "8px",
                      color: "black",
                    }}
                  >
                    Sample Claim
                  </td>
                  <td
                    style={{
                      border: "1px solid black",
                      padding: "8px",
                      color: "black",
                    }}
                  >
                    Sample Subject
                  </td>
                  <td
                    style={{
                      border: "1px solid black",
                      padding: "8px",
                      color: "black",
                    }}
                  >
                    Sample Person
                  </td>
                  <td
                    style={{
                      border: "1px solid black",
                      padding: "8px",
                      color: "black",
                    }}
                  >
                    tag1, tag2
                  </td>
                  <td
                    style={{
                      border: "1px solid black",
                      padding: "8px",
                      color: "black",
                    }}
                  >
                    http://example.com/image.jpg
                  </td>
                  <td
                    style={{
                      border: "1px solid black",
                      padding: "8px",
                      color: "black",
                    }}
                  >
                    http://example.com/image2.jpg
                  </td>
                </tr>
              </tbody>
            </table>
          </Box>
        </div>
      ) : (
        <Formik
          onSubmit={handleFormSubmit}
          initialValues={initialValues}
          validationSchema={validationSchema}
        >
          {({
            values,
            errors,
            touched,
            handleBlur,
            handleChange,
            handleSubmit,
          }) => (
            <form id="form-id" onSubmit={handleSubmit}>
              <Box display="flex" flexDirection="column" gap="20px">
                <TextField
                  fullWidth
                  variant="outlined"
                  type="text"
                  label="Story Date"
                  onBlur={handleBlur}
                  onChange={handleChange}
                  value={values.Story_Date}
                  name="Story_Date"
                  error={!!touched.Story_Date && !!errors.Story_Date}
                  helperText={touched.Story_Date && errors.Story_Date}
                  InputLabelProps={{
                    style: { color: "black" },
                  }}
                  inputProps={{
                    style: { color: "black" },
                  }}
                  sx={{
                    "& .MuiOutlinedInput-root": {
                      "& fieldset": {
                        borderColor: "black",
                      },
                      "&:hover fieldset": {
                        borderColor: "black",
                      },
                      "&.Mui-focused fieldset": {
                        borderColor: "black",
                      },
                    },
                    "& .MuiInputLabel-root.Mui-focused": {
                      color: "black",
                    },
                  }}
                />
                <TextField
                  fullWidth
                  variant="outlined"
                  type="text"
                  label="Story URL"
                  onBlur={handleBlur}
                  onChange={handleChange}
                  value={values.Story_URL}
                  name="Story_URL"
                  error={!!touched.Story_URL && !!errors.Story_URL}
                  helperText={touched.Story_URL && errors.Story_URL}
                  InputLabelProps={{
                    style: { color: "black" },
                  }}
                  inputProps={{
                    style: { color: "black" },
                  }}
                  sx={{
                    "& .MuiOutlinedInput-root": {
                      "& fieldset": {
                        borderColor: "black",
                      },
                      "&:hover fieldset": {
                        borderColor: "black",
                      },
                      "&.Mui-focused fieldset": {
                        borderColor: "black",
                      },
                    },
                    "& .MuiInputLabel-root.Mui-focused": {
                      color: "black",
                    },
                  }}
                />
                <TextField
                  fullWidth
                  variant="outlined"
                  type="text"
                  label="Headline"
                  onBlur={handleBlur}
                  onChange={handleChange}
                  value={values.Headline}
                  name="Headline"
                  error={!!touched.Headline && !!errors.Headline}
                  helperText={touched.Headline && errors.Headline}
                  InputLabelProps={{
                    style: { color: "black" },
                  }}
                  inputProps={{
                    style: { color: "black" },
                  }}
                  sx={{
                    "& .MuiOutlinedInput-root": {
                      "& fieldset": {
                        borderColor: "black",
                      },
                      "&:hover fieldset": {
                        borderColor: "black",
                      },
                      "&.Mui-focused fieldset": {
                        borderColor: "black",
                      },
                    },
                    "& .MuiInputLabel-root.Mui-focused": {
                      color: "black",
                    },
                  }}
                />
                <TextField
                  fullWidth
                  variant="outlined"
                  type="text"
                  label="Tags"
                  onBlur={handleBlur}
                  onChange={handleChange}
                  value={values.tags}
                  name="tags"
                  error={!!touched.tags && !!errors.tags}
                  helperText={touched.tags && errors.tags}
                  InputLabelProps={{
                    style: { color: "black" },
                  }}
                  inputProps={{
                    style: { color: "black" },
                  }}
                  sx={{
                    "& .MuiOutlinedInput-root": {
                      "& fieldset": {
                        borderColor: "black",
                      },
                      "&:hover fieldset": {
                        borderColor: "black",
                      },
                      "&.Mui-focused fieldset": {
                        borderColor: "black",
                      },
                    },
                    "& .MuiInputLabel-root.Mui-focused": {
                      color: "black",
                    },
                  }}
                />
                <TextField
                  fullWidth
                  variant="outlined"
                  type="text"
                  label="What (Claim)"
                  onBlur={handleBlur}
                  onChange={handleChange}
                  value={values["What_(Claim)"]}
                  name="What_(Claim)"
                  error={!!touched["What_(Claim)"] && !!errors["What_(Claim)"]}
                  helperText={touched["What_(Claim)"] && errors["What_(Claim)"]}
                  InputLabelProps={{
                    style: { color: "black" },
                  }}
                  inputProps={{
                    style: { color: "black" },
                  }}
                  sx={{
                    "& .MuiOutlinedInput-root": {
                      "& fieldset": {
                        borderColor: "black",
                      },
                      "&:hover fieldset": {
                        borderColor: "black",
                      },
                      "&.Mui-focused fieldset": {
                        borderColor: "black",
                      },
                    },
                    "& .MuiInputLabel-root.Mui-focused": {
                      color: "black",
                    },
                  }}
                />
                <FieldArray name="img">
                  {({ push, remove }) => (
                    <div>
                      {values.img.map((imageUrl, index) => (
                        <Box key={index} display="flex" alignItems="center">
                          <TextField
                            fullWidth
                            variant="outlined"
                            type="text"
                            label={`Image URL ${index + 1}`}
                            onBlur={handleBlur}
                            onChange={handleChange}
                            value={imageUrl}
                            name={`img[${index}]`}
                            error={
                              !!touched.img &&
                              !!errors.img &&
                              !!errors.img[index]
                            }
                            helperText={
                              touched.img && !!errors.img && errors.img[index]
                            }
                            InputLabelProps={{
                              style: { color: "black" },
                            }}
                            inputProps={{
                              style: { color: "black" },
                            }}
                            sx={{
                              "& .MuiOutlinedInput-root": {
                                "& fieldset": {
                                  borderColor: "black",
                                },
                                "&:hover fieldset": {
                                  borderColor: "black",
                                },
                                "&.Mui-focused fieldset": {
                                  borderColor: "black",
                                },
                              },
                              "& .MuiInputLabel-root.Mui-focused": {
                                color: "black",
                              },
                            }}
                          />
                          <IconButton
                            onClick={() => remove(index)}
                            size="small"
                            sx={{ ml: 2 }}
                          >
                            <CloseIcon />
                          </IconButton>
                        </Box>
                      ))}
                      <Button
                        type="button"
                        onClick={() => push("")}
                        variant="outlined"
                        sx={{
                          mt: 2,
                          color: "black",
                          borderColor: "black",
                          "&:hover": {
                            borderColor: "black",
                          },
                        }}
                      >
                        Add Image URL
                      </Button>
                    </div>
                  )}
                </FieldArray>
                <TextField
                  fullWidth
                  variant="outlined"
                  type="text"
                  label="About Person"
                  onBlur={handleBlur}
                  onChange={handleChange}
                  value={values.About_Person}
                  name="About_Person"
                  error={!!touched.About_Person && !!errors.About_Person}
                  helperText={touched.About_Person && errors.About_Person}
                  InputLabelProps={{
                    style: { color: "black" },
                  }}
                  inputProps={{
                    style: { color: "black" },
                  }}
                  sx={{
                    "& .MuiOutlinedInput-root": {
                      "& fieldset": {
                        borderColor: "black",
                      },
                      "&:hover fieldset": {
                        borderColor: "black",
                      },
                      "&.Mui-focused fieldset": {
                        borderColor: "black",
                      },
                    },
                    "& .MuiInputLabel-root.Mui-focused": {
                      color: "black",
                    },
                  }}
                />
                <TextField
                  fullWidth
                  variant="outlined"
                  type="text"
                  label="About Subject"
                  onBlur={handleBlur}
                  onChange={handleChange}
                  value={values.About_Subject}
                  name="About_Subject"
                  error={!!touched.About_Subject && !!errors.About_Subject}
                  helperText={touched.About_Subject && errors.About_Subject}
                  InputLabelProps={{
                    style: { color: "black" },
                  }}
                  inputProps={{
                    style: { color: "black" },
                  }}
                  sx={{
                    "& .MuiOutlinedInput-root": {
                      "& fieldset": {
                        borderColor: "black",
                      },
                      "&:hover fieldset": {
                        borderColor: "black",
                      },
                      "&.Mui-focused fieldset": {
                        borderColor: "black",
                      },
                    },
                    "& .MuiInputLabel-root.Mui-focused": {
                      color: "black",
                    },
                  }}
                />
              </Box>
            </form>
          )}
        </Formik>
      )}
      <Box display="flex" justifyContent="space-between" mt={4}>
        {view === "form" ? (
          <Button
            type="submit"
            form="form-id"
            color="primary"
            variant="contained"
            sx={{
              backgroundColor: colors.blueAccent[600],
              color: "#fff",
              fontSize: "14px",
              fontWeight: "bold",
              padding: "10px 20px",
            }}
          >
            Submit Form
          </Button>
        ) : (
          <Button
            onClick={handleCSVSubmit}
            color="primary"
            variant="contained"
            sx={{
              backgroundColor: colors.blueAccent[600],
              color: "#fff",
              fontSize: "14px",
              fontWeight: "bold",
              padding: "10px 20px",
            }}
          >
            Submit CSV
          </Button>
        )}

        <Button
          onClick={handleLogout}
          color="secondary"
          variant="contained"
          sx={{
            backgroundColor: colors.redAccent[400],
            color: "#fff",
            fontSize: "14px",
            fontWeight: "bold",
            padding: "10px 20px",
          }}
        >
          Log Out
        </Button>
      </Box>

      <Typography
        variant="h6"
        sx={{
          mt: 2,
          color: isError ? "red" : "green",
          fontWeight: "bold",
          fontSize: "1.2rem",
        }}
      >
        {message}
      </Typography>
    </Box>
  );
};

export default Form;
