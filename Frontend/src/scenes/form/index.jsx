import { React, useContext } from "react";
import { Box, Button, TextField, Typography, useTheme } from "@mui/material";
import { Formik } from "formik";
import * as yup from "yup";
import { useState } from "react";
import { tokens } from "../../theme";
import { Link, useNavigate } from "react-router-dom";
import { AuthContext } from '../../context/AuthContext';  // Import AuthContext

const Form = () => {
  const { isAuthenticated, setIsAuthenticated } = useContext(AuthContext);

    const [message, setMessage] = useState("");
    const [isError, setIsError] = useState(false);
  const navigate = useNavigate();

  const handleFormSubmit = async (values) => {
    try {
      const response = await fetch(
        // "/api/appendData",
        "/api/appendData",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            charset: "utf-8",
          },
          body: JSON.stringify(values),
        }
      );

      if (response.ok) {
        const result = await response.json();
        console.log(result.message); // Or set some state to show a success message
             setMessage(result.message);
             setIsError(false);
      } else {
        console.error("Submission failed", await response.text());
         setMessage(
           response.message || "Submission failed, please check your input."
         );
         setIsError(true);
      }
    } catch (error) {
      console.error("An error occurred during submission:", error);
 setMessage(`An error occurred during submission: ${error.message}`);
 setIsError(true);    }
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
      credentials: "include", // Ensure cookies are sent with the request
    });

    if (response.ok) {
      setIsAuthenticated(false); // Make sure to set authentication to false
      navigate("/login");
    } else {
      throw new Error("Failed to logout");
    }
  } catch (error) {
    alert("Failed to logout");

    navigate("/login");
  }
};

  return (
    <Box m="20px">
      <Typography variant="h2" component="h1" align="center" gutterBottom>
        Add your claim
      </Typography>
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
          <form onSubmit={handleSubmit}>
            <Box display="flex" flexDirection="column" gap="20px">
              <TextField
                fullWidth
                variant="filled"
                type="text"
                label="Story Date"
                onBlur={handleBlur}
                onChange={handleChange}
                value={values.Story_Date}
                name="Story_Date"
                error={!!touched.Story_Date && !!errors.Story_Date}
                helperText={touched.Story_Date && errors.Story_Date}
              />
              <TextField
                fullWidth
                variant="filled"
                type="text"
                label="Story URL"
                onBlur={handleBlur}
                onChange={handleChange}
                value={values.Story_URL}
                name="Story_URL"
                error={!!touched.Story_URL && !!errors.Story_URL}
                helperText={touched.Story_URL && errors.Story_URL}
              />
              <TextField
                fullWidth
                variant="filled"
                type="text"
                label="Headline"
                onBlur={handleBlur}
                onChange={handleChange}
                value={values.Headline}
                name="Headline"
                error={!!touched.Headline && !!errors.Headline}
                helperText={touched.Headline && errors.Headline}
              />
              {/* <TextField
                fullWidth
                variant="filled"
                type="text"
                label="Claim URL"
                onBlur={handleBlur}
                onChange={handleChange}
                value={values.Claim_URL}
                name="Claim_URL"
                error={!!touched.Claim_URL && !!errors.Claim_URL}
                helperText={touched.Claim_URL && errors.Claim_URL}
              /> */}
              <TextField
                fullWidth
                variant="filled"
                type="text"
                label="Tags"
                onBlur={handleBlur}
                onChange={handleChange}
                value={values.tags}
                name="tags"
                error={!!touched.tags && !!errors.tags}
                helperText={touched.tags && errors.tags}
              />
              <TextField
                fullWidth
                variant="filled"
                type="text"
                label="What (Claim)"
                onBlur={handleBlur}
                onChange={handleChange}
                value={values["What_(Claim)"]}
                name="What_(Claim)"
                error={!!touched["What_(Claim)"] && !!errors["What_(Claim)"]}
                helperText={touched["What_(Claim)"] && errors["What_(Claim)"]}
              />
              <TextField
                fullWidth
                variant="filled"
                type="text"
                label="Image URL"
                onBlur={handleBlur}
                onChange={handleChange}
                value={values.img}
                name="img"
                error={!!touched.img && !!errors.img}
                helperText={touched.img && errors.img}
              />
              <TextField
                fullWidth
                variant="filled"
                type="text"
                label="About Person"
                onBlur={handleBlur}
                onChange={handleChange}
                value={values.About_Person}
                name="About_Person"
                error={!!touched.About_Person && !!errors.About_Person}
                helperText={touched.About_Person && errors.About_Person}
              />
              <TextField
                fullWidth
                variant="filled"
                type="text"
                label="About Subject"
                onBlur={handleBlur}
                onChange={handleChange}
                value={values.About_Subject}
                name="About_Subject"
                error={!!touched.About_Subject && !!errors.About_Subject}
                helperText={touched.About_Subject && errors.About_Subject}
              />
            </Box>
            <Box display="flex" justifyContent="space-between" mt={4}>
              <Button
                type="submit"
                color="primary"
                variant="contained"
                sx={{
                  backgroundColor: colors.blueAccent[600],
                  color: colors.grey[100],
                  fontSize: "14px",
                  fontWeight: "bold",
                  padding: "10px 20px",
                }}
              >
                Submit
              </Button>
              <Button
                onClick={handleLogout}
                color="secondary"
                variant="contained"
                sx={{
                  backgroundColor: colors.redAccent[400],
                  color: colors.grey[100],
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
          </form>
        )}
      </Formik>
    </Box>
  );
};

const validationSchema = yup.object().shape({
  Story_Date: yup.string().required("Story date is required"),
  Story_URL: yup
    .string()
    .url("Enter a valid URL")
    .required("Story URL is required"),
  Headline: yup.string().required("Headline is required"),
  "What_(Claim)": yup.string().required("Claim is required"), // Use the key as a string literal
  img: yup
    .string()
    .url("Enter a valid image URL")
    .required("Image URL is required"),
  About_Person: yup.string().notRequired(),
  About_Subject: yup.string().required("Subject is required"),
});


const initialValues = {
  Story_Date: "",
  Story_URL: "",
  Headline: "",
  "What_(Claim)": "",
  tags: "",
  img: "",
  About_Person: "",
  About_Subject: "",
};

export default Form;
