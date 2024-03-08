import React from "react";
import { Box, Button, TextField, Typography } from "@mui/material";
import { Formik } from "formik";
import * as yup from "yup";

const Form = () => {
  const handleFormSubmit = async (values) => {
    try {
      const response = await fetch("http://127.0.0.1:8080/appendData", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "charset":"utf-8",
        },
        body: JSON.stringify(values),
      });

      if (response.ok) {
        const result = await response.json();
        console.log(result.message); // Or set some state to show a success message
      } else {
        console.error("Submission failed", await response.text());
        // Handle server errors or invalid responses here
        // For example, set an error state to display an error message
      }
    } catch (error) {
      console.error("An error occurred during submission:", error);
      // Handle the error state here
    }
  };


  return (
    <Box m="20px">
      <Typography variant="h2" component="h1" align="center" gutterBottom>
        Claim
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
              <TextField
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
              />
              <TextField
                fullWidth
                variant="filled"
                type="text"
                label="What (Claim)"
                onBlur={handleBlur}
                onChange={handleChange}
                value={values.What_Claim}
                name="What_Claim"
                error={!!touched.What_Claim && !!errors.What_Claim}
                helperText={touched.What_Claim && errors.What_Claim}
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
            <Button
              type="submit"
              color="primary"
              variant="contained"
              sx={{ mt: 2 }}
            >
              Submit
            </Button>
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
  Claim_URL: yup
    .string()
    .url("Enter a valid URL")
    .required("Claim URL is required"),
  What_Claim: yup.string().required("Claim is required"),
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
  Claim_URL: "",
  What_Claim: "",
  img: "",
  About_Person: "",
  About_Subject: "",
};

export default Form;
