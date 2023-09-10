# Setup

```bash
PHONE_NUMBER=1234567890
EMAIL_ADDRESS=john@doe.com
sed "s/PHONE_NUMBER_PLACEHOLDER/$PHONE_NUMBER/g" resume.tex > resume_temp.tex
sed "s/EMAIL_ADDRESS_PLACEHOLDER/$EMAIL_ADDRESS/g" resume_temp.tex > resume_replaced.tex
rm resume_replaced.pdf
pdflatex -interaction=nonstopmode resume_replaced.tex 
open resume_replaced.pdf
rm resume_temp.tex
rm resume_replaced.tex
```
