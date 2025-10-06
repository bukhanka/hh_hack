API Reference
Tavily Search

Execute a search query using Tavily Search.
POST
/
search
Authorizations
​
Authorization
string
header
required

Bearer authentication header in the form Bearer <token>, where <token> is your Tavily API key (e.g., Bearer tvly-YOUR_API_KEY).
Body
application/json

Parameters for the Tavily Search request.
​
query
string
required

The search query to execute with Tavily.
Example:

"who is Leo Messi?"
​
auto_parameters
boolean
default:false

When auto_parameters is enabled, Tavily automatically configures search parameters based on your query's content and intent. You can still set other parameters manually, and your explicit values will override the automatic ones. The parameters include_answer, include_raw_content, and max_results must always be set manually, as they directly affect response size. Note: search_depth may be automatically set to advanced when it's likely to improve results. This uses 2 API credits per request. To avoid the extra cost, you can explicitly set search_depth to basic. Currently in beta.
​
topic
enum<string>
default:general

The category of the search.news is useful for retrieving real-time updates, particularly about politics, sports, and major current events covered by mainstream media sources. general is for broader, more general-purpose searches that may include a wide range of sources.
Available options: general, 
news, 
finance 
​
search_depth
enum<string>
default:basic

The depth of the search. advanced search is tailored to retrieve the most relevant sources and content snippets for your query, while basic search provides generic content snippets from each source. A basic search costs 1 API Credit, while an advanced search costs 2 API Credits.
Available options: basic, 
advanced 
​
chunks_per_source
integer
default:3

Chunks are short content snippets (maximum 500 characters each) pulled directly from the source. Use chunks_per_source to define the maximum number of relevant chunks returned per source and to control the content length. Chunks will appear in the content field as: <chunk 1> [...] <chunk 2> [...] <chunk 3>. Available only when search_depth is advanced.
Required range: 1 <= x <= 3
​
max_results
integer
default:5

The maximum number of search results to return.
Required range: 0 <= x <= 20
Example:

1
​
time_range
enum<string>

The time range back from the current date to filter results ( publish date ). Useful when looking for sources that have published data.
Available options: day, 
week, 
month, 
year, 
d, 
w, 
m, 
y 
​
days
integer
default:7

Number of days back from the current date to include ( publish date ). Available only if topic is news.
Required range: x >= 1
​
start_date
string

Will return all results after the specified start date ( publish date ). Required to be written in the format YYYY-MM-DD
Example:

"2025-02-09"
​
end_date
string

Will return all results before the specified end date ( publish date ). Required to be written in the format YYYY-MM-DD
Example:

"2000-01-28"
​
include_answer
default:false

Include an LLM-generated answer to the provided query. basic or true returns a quick answer. advanced returns a more detailed answer.
​
include_raw_content
default:false

Include the cleaned and parsed HTML content of each search result. markdown or true returns search result content in markdown format. text returns the plain text from the results and may increase latency.
​
include_images
boolean
default:false

Also perform an image search and include the results in the response.
​
include_image_descriptions
boolean
default:false

When include_images is true, also add a descriptive text for each image.
​
include_favicon
boolean
default:false

Whether to include the favicon URL for each result.
​
include_domains
string[]

A list of domains to specifically include in the search results. Maximum 300 domains.
​
exclude_domains
string[]

A list of domains to specifically exclude from the search results. Maximum 150 domains.
​
country
enum<string>

Boost search results from a specific country. This will prioritize content from the selected country in the search results. Available only if topic is general.
Available options: afghanistan, 
albania, 
algeria, 
andorra, 
angola, 
argentina, 
armenia, 
australia, 
austria, 
azerbaijan, 
bahamas, 
bahrain, 
bangladesh, 
barbados, 
belarus, 
belgium, 
belize, 
benin, 
bhutan, 
bolivia, 
bosnia and herzegovina, 
botswana, 
brazil, 
brunei, 
bulgaria, 
burkina faso, 
burundi, 
cambodia, 
cameroon, 
canada, 
cape verde, 
central african republic, 
chad, 
chile, 
china, 
colombia, 
comoros, 
congo, 
costa rica, 
croatia, 
cuba, 
cyprus, 
czech republic, 
denmark, 
djibouti, 
dominican republic, 
ecuador, 
egypt, 
el salvador, 
equatorial guinea, 
eritrea, 
estonia, 
ethiopia, 
fiji, 
finland, 
france, 
gabon, 
gambia, 
georgia, 
germany, 
ghana, 
greece, 
guatemala, 
guinea, 
haiti, 
honduras, 
hungary, 
iceland, 
india, 
indonesia, 
iran, 
iraq, 
ireland, 
israel, 
italy, 
jamaica, 
japan, 
jordan, 
kazakhstan, 
kenya, 
kuwait, 
kyrgyzstan, 
latvia, 
lebanon, 
lesotho, 
liberia, 
libya, 
liechtenstein, 
lithuania, 
luxembourg, 
madagascar, 
malawi, 
malaysia, 
maldives, 
mali, 
malta, 
mauritania, 
mauritius, 
mexico, 
moldova, 
monaco, 
mongolia, 
montenegro, 
morocco, 
mozambique, 
myanmar, 
namibia, 
nepal, 
netherlands, 
new zealand, 
nicaragua, 
niger, 
nigeria, 
north korea, 
north macedonia, 
norway, 
oman, 
pakistan, 
panama, 
papua new guinea, 
paraguay, 
peru, 
philippines, 
poland, 
portugal, 
qatar, 
romania, 
russia, 
rwanda, 
saudi arabia, 
senegal, 
serbia, 
singapore, 
slovakia, 
slovenia, 
somalia, 
south africa, 
south korea, 
south sudan, 
spain, 
sri lanka, 
sudan, 
sweden, 
switzerland, 
syria, 
taiwan, 
tajikistan, 
tanzania, 
thailand, 
togo, 
trinidad and tobago, 
tunisia, 
turkey, 
turkmenistan, 
uganda, 
ukraine, 
united arab emirates, 
united kingdom, 
united states, 
uruguay, 
uzbekistan, 
venezuela, 
vietnam, 
yemen, 
zambia, 
zimbabwe 
Response

Search results returned successfully
​
query
string
required

The search query that was executed.
Example:

"Who is Leo Messi?"
​
answer
string
required

A short answer to the user's query, generated by an LLM. Included in the response only if include_answer is requested (i.e., set to true, basic, or advanced)
Example:

"Lionel Messi, born in 1987, is an Argentine footballer widely regarded as one of the greatest players of his generation. He spent the majority of his career playing for FC Barcelona, where he won numerous domestic league titles and UEFA Champions League titles. Messi is known for his exceptional dribbling skills, vision, and goal-scoring ability. He has won multiple FIFA Ballon d'Or awards, numerous La Liga titles with Barcelona, and holds the record for most goals scored in a calendar year. In 2014, he led Argentina to the World Cup final, and in 2015, he helped Barcelona capture another treble. Despite turning 36 in June, Messi remains highly influential in the sport."
​
images
object[]
required

List of query-related images. If include_image_descriptions is true, each item will have url and description.

Show child attributes

Show child attributes
Example:

[]

​
results
object[]
required

A list of sorted search results, ranked by relevancy.

Show child attributes

Show child attributes

​
response_time
number
required

Time in seconds it took to complete the request.
Example:

"1.67"
​
auto_parameters
object

A dictionary of the selected auto_parameters, only shown when auto_parameters is true.
Example:

{
  "topic": "general",
  "search_depth": "basic"
}

​
request_id
string

A unique request identifier you can share with customer support to help resolve issues with specific requests.
Example:

"123e4567-e89b-12d3-a456-426614174111"
Introduction
Tavily Extract
x
github
linkedin
website


https://docs.tavily.com/documentation/api-reference/endpoint/search