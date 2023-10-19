##### Python script to run Defender adavance threat hunting query and upload to sumologic

Requirements:
1. Azure app  registration with approrpiate permission to read defendner logs (API Permission - AdvancedQuery.Read.All)
2. Sumologic hosted http collector
3. Environment variables for
   1. Azure tenant ID
   2. app client ID
   3. app secret
   4. sumologic collector url
4. In Sumologic collector use multiline processing and apply regex boundary {in "Advanced Options for Logs (Optional)" section of the collector properties}
5. The regex boundary needs to be RE2 compliant
6. In this case regex is (?m)^.*$
7. Which means its a multiline ((?m)) input, capture everything(^.*) until end of line ($)