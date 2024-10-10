import React from "react";
import { Box, Typography, Container, Card, CardContent } from "@mui/material";
import { useTranslation } from "react-i18next";

const About = () => {
  const { t } = useTranslation(); // Hook for translations

  return (
    <Container maxWidth="xl">
      <Box mt={5} mb={2}>
        <Box m="20px">
          <Box
            display="flex"
            justifyContent="space-between"
            alignItems="center"
          >
            <Typography
              variant="h2"
              gutterBottom
              sx={{ color: "black", fontWeight: "bold" }}
            >
              {t("about")} {/* 'About' */}
            </Typography>
          </Box>
        </Box>

        <Card
          sx={{
            backgroundColor: "rgba(245, 245, 245, 0.8)",
            boxShadow: 3,
            padding: 4,
          }}
        >
          <CardContent>
            <Typography
              variant="h5"
              gutterBottom
              sx={{ color: "black", fontWeight: "bold" }}
            >
              {t("about_title")} {/* 'Welcome to MESSAGE CHECK!' */}
            </Typography>

            <Typography
              variant="body1"
              paragraph
              sx={{ color: "black", fontFamily: "Arial, sans-serif" }}
            >
              {t("about_description")} {/* MESSAGE CHECK description */}
            </Typography>

            <Typography
              variant="h5"
              gutterBottom
              sx={{ color: "black", fontWeight: "bold" }}
            >
              {t("explanatory_note")} {/* Explanatory note */}
            </Typography>

            <Typography
              variant="body2"
              paragraph
              sx={{
                color: "black",
                fontFamily: "Arial, sans-serif",
                fontStyle: "italic",
              }}
            >
              {t("processing_database")}{" "}
              {/* Processing the Vishvas News database */}
            </Typography>

            <Typography
              variant="body2"
              paragraph
              sx={{
                color: "black",
                fontFamily: "Arial, sans-serif",
                fontStyle: "italic",
              }}
            >
              {t("text_queries")} {/* Text Queries in English */}
            </Typography>

            <Typography
              variant="body2"
              paragraph
              sx={{
                color: "black",
                fontFamily: "Arial, sans-serif",
                fontStyle: "italic",
              }}
            >
              {t("models_reason")} {/* Reasons for models used */}
            </Typography>

            <Typography
              variant="body2"
              paragraph
              sx={{
                color: "black",
                fontFamily: "Arial, sans-serif",
                fontStyle: "italic",
              }}
            >
              {t("note_bert_score")} {/* BERTScore model explanation */}
            </Typography>

            <Typography
              variant="body2"
              paragraph
              sx={{
                color: "black",
                fontFamily: "Arial, sans-serif",
                fontStyle: "italic",
              }}
            >
              {t("merge_lists")} {/* Merging the ranked lists */}
            </Typography>

            <Typography
              variant="body2"
              paragraph
              sx={{
                color: "black",
                fontFamily: "Arial, sans-serif",
                fontStyle: "italic",
              }}
            >
              {t("multilingual_queries")} {/* Handling multilingual queries */}
            </Typography>

            <Typography
              variant="body2"
              paragraph
              sx={{
                color: "black",
                fontFamily: "Arial, sans-serif",
                fontStyle: "italic",
              }}
            >
              {t("image_query")} {/* Image query processing */}
            </Typography>

            <Typography
              variant="h5"
              gutterBottom
              sx={{ color: "blue", fontWeight: "bold" }}
            >
              <a
                href="https://www.vishvasnews.com/about-us/"
                target="_blank"
                rel="noopener noreferrer"
                style={{ color: "inherit", textDecoration: "none" }}
              >
                {t("about_vishvas_news")} {/* About Vishvas News */}
              </a>
            </Typography>

            <Typography
              variant="body1"
              paragraph
              sx={{
                color: "black",
                fontFamily: "Arial, sans-serif",
                fontWeight: "bold",
              }}
            >
              {t("contact_us")} {/* Contact Us */}
            </Typography>

            <Typography
              variant="body1"
              paragraph
              sx={{ color: "black", fontFamily: "Arial, sans-serif" }}
            >
              {t("query_feedback")} {/* Contact email */}
            </Typography>

            <Typography
              variant="body1"
              paragraph
              sx={{ color: "black", fontFamily: "Arial, sans-serif" }}
            >
              {t("contact_whatsapp")} {/* WhatsApp contact */}
            </Typography>
          </CardContent>
        </Card>
      </Box>
    </Container>
  );
};

export default About;
