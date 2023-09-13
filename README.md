# Setup

```bash
PHONE_NUMBER=1234567890
EMAIL_ADDRESS=john@doe.com
HOMEPAGE=home.johndoe.com
sed "s/PHONE_NUMBER_PLACEHOLDER/$PHONE_NUMBER/g" resume.tex > resume_1.tex
sed "s/HOMEPAGE_PLACEHOLDER/$HOMEPAGE/g" resume_1.tex > resume_2.tex
sed "s/EMAIL_ADDRESS_PLACEHOLDER/$EMAIL_ADDRESS/g" resume_2.tex > resume_replaced.tex
rm resume_replaced.pdf
pdflatex -interaction=nonstopmode resume_replaced.tex 
open resume_replaced.pdf
rm resume_1.tex
rm resume_2.tex
rm resume_temp.tex
rm resume_replaced.tex
```
