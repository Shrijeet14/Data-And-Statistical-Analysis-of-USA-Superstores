import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.figure_factory as ff
import warnings

warnings.filterwarnings('ignore')

st.set_page_config(page_title="Data Analysis of Superstores", page_icon=":bar_chart:", layout="wide")
st.title(":bar_chart: Data Analysis of Superstores")

st.markdown('<style>div.block-container{padding-top:1rem;}</style>', unsafe_allow_html=True)

# fl = st.file_uploader(":file_folder: Upload Your File", type=["csv", "txt", "xlsx", "xls"])

# if fl is not None:
filename = "Superstore.csv"
# st.write(filename)
df = pd.read_excel(filename)

df["Order Date"] = pd.to_datetime(df["Order Date"])

# Getting the min and max date
startDate = pd.to_datetime(df["Order Date"]).min()
endDate = pd.to_datetime(df["Order Date"]).max()

st.sidebar.header("Filters")
date1 = pd.to_datetime(st.sidebar.date_input("Start Date", startDate))
date2 = pd.to_datetime(st.sidebar.date_input("End Date", endDate))

# Filter data by date
df = df[(df["Order Date"] >= date1) & (df["Order Date"] <= date2)].copy()

# Filter by region
region = st.sidebar.multiselect("Pick your Region", df["Region"].unique())
df_region = df if not region else df[df["Region"].isin(region)]

# Filter by state
state = st.sidebar.multiselect("Pick your State", df_region["State"].unique())
df_state = df_region if not state else df_region[df_region["State"].isin(state)]

# Filter by city
city = st.sidebar.multiselect("Pick the City", df_state["City"].unique())
filtered_df = df_state if not city else df_state[df_state["City"].isin(city)]

col1, col2 = st.columns(2)

# Category wise Sales
category_df = filtered_df.groupby("Category")["Sales"].sum().reset_index()
with col1:
    st.subheader("Category wise Sales")
    fig = px.bar(category_df, x="Category", y="Sales", text=category_df["Sales"].apply(lambda x: f'${x:,.2f}'),
                    template="seaborn")
    st.plotly_chart(fig, use_container_width=True)

# Region wise Sales
with col2:
    st.subheader("Region wise Sales")
    fig = px.pie(filtered_df, values="Sales", names="Region", hole=0.5)
    fig.update_traces(textinfo='percent+label', textposition='outside')
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

cl1, cl2 = st.columns(2)
with cl1:
    with st.expander("Category View Data"):
        st.write(category_df.style.background_gradient(cmap="Blues"))
        csv = category_df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Data", data=csv, file_name="Category.csv", mime="text/csv")

with cl2:
    with st.expander("Region View Data"):
        region_df = filtered_df.groupby("Region")["Sales"].sum().reset_index()
        st.write(region_df.style.background_gradient(cmap="Oranges"))
        csv = region_df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Data", data=csv, file_name="Region.csv", mime="text/csv")

st.markdown("---")

# Time Series Analysis
filtered_df["month_year"] = filtered_df["Order Date"].dt.to_period("M")
st.subheader('Time Series Analysis')
linechart = filtered_df.groupby(filtered_df["month_year"].dt.strftime("%Y-%b"))["Sales"].sum().reset_index()
fig2 = px.line(linechart, x="month_year", y="Sales", labels={"Sales": "Amount"}, template="plotly_white")
st.plotly_chart(fig2, use_container_width=True)

with st.expander("View Data of TimeSeries"):
    st.write(linechart.T.style.background_gradient(cmap="Blues"))
    csv = linechart.to_csv(index=False).encode("utf-8")
    st.download_button('Download Data', data=csv, file_name="TimeSeries.csv", mime='text/csv')

st.markdown("---")

# Hierarchical view of Sales using TreeMap
st.subheader("Hierarchical view of Sales using TreeMap")
fig3 = px.treemap(filtered_df, path=["Region", "Category", "Sub-Category"], values="Sales",
                    color="Sub-Category", hover_data=["Sales"], template="plotly")
st.plotly_chart(fig3, use_container_width=True)

st.markdown("---")

chart1, chart2 = st.columns(2)
with chart1:
    st.subheader('Segment wise Sales')
    fig = px.pie(filtered_df, values="Sales", names="Segment", template="plotly_dark")
    fig.update_traces(textinfo='percent+label', textposition='inside')
    st.plotly_chart(fig, use_container_width=True)

with chart2:
    st.subheader('Category wise Sales')
    fig = px.pie(filtered_df, values="Sales", names="Category", template="gridon")
    fig.update_traces(textinfo='percent+label', textposition='inside')
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Month wise Sub-Category Sales Summary
st.subheader(":point_right: Month wise Sub-Category Sales Summary")
with st.expander("Summary Table"):
    df_sample = df[["Region", "State", "City", "Category", "Sales", "Profit", "Quantity"]].head()
    fig = ff.create_table(df_sample, colorscale="Cividis")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("Month wise sub-Category Table")
    filtered_df["month"] = filtered_df["Order Date"].dt.month_name()
    sub_category_Year = pd.pivot_table(filtered_df, values="Sales", index=["Sub-Category"], columns="month")
    st.write(sub_category_Year.style.background_gradient(cmap="Blues"))

st.markdown("---")

# Scatter plot
st.subheader("Relationship between Sales and Profits using Scatter Plot")
fig4 = px.scatter(filtered_df, x="Sales", y="Profit", size="Quantity", template="plotly")
fig4.update_layout(title="Relationship between Sales and Profits", titlefont=dict(size=20),
                    xaxis=dict(title="Sales", titlefont=dict(size=19)),
                    yaxis=dict(title="Profit", titlefont=dict(size=19)))
st.plotly_chart(fig4, use_container_width=True)

with st.expander("View Data"):
    st.write(filtered_df.iloc[:500, 1:20:2].style.background_gradient(cmap="Oranges"))

# Sales and Profit by Sub-Category
st.subheader("Sales and Profit by Sub-Category")
sub_category_df = filtered_df.groupby("Sub-Category")[["Sales", "Profit"]].sum().reset_index()
fig5 = px.bar(sub_category_df, x="Sub-Category", y=["Sales", "Profit"], barmode="group", template="plotly_white")
st.plotly_chart(fig5, use_container_width=True)

st.markdown("---")

st.subheader("Sales Distribution by State")
us_state_abbrev = {
'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR', 'California': 'CA',
'Colorado': 'CO', 'Connecticut': 'CT', 'Delaware': 'DE', 'Florida': 'FL', 'Georgia': 'GA',
'Hawaii': 'HI', 'Idaho': 'ID', 'Illinois': 'IL', 'Indiana': 'IN', 'Iowa': 'IA', 'Kansas': 'KS',
'Kentucky': 'KY', 'Louisiana': 'LA', 'Maine': 'ME', 'Maryland': 'MD', 'Massachusetts': 'MA',
'Michigan': 'MI', 'Minnesota': 'MN', 'Mississippi': 'MS', 'Missouri': 'MO', 'Montana': 'MT',
'Nebraska': 'NE', 'Nevada': 'NV', 'New Hampshire': 'NH', 'New Jersey': 'NJ', 'New Mexico': 'NM',
'New York': 'NY', 'North Carolina': 'NC', 'North Dakota': 'ND', 'Ohio': 'OH', 'Oklahoma': 'OK',
'Oregon': 'OR', 'Pennsylvania': 'PA', 'Rhode Island': 'RI', 'South Carolina': 'SC', 'South Dakota': 'SD',
'Tennessee': 'TN', 'Texas': 'TX', 'Utah': 'UT', 'Vermont': 'VT', 'Virginia': 'VA', 'Washington': 'WA',
'West Virginia': 'WV', 'Wisconsin': 'WI', 'Wyoming': 'WY'
}


state_sales = filtered_df.groupby("State")["Sales"].sum().reset_index()
state_sales["State"] = state_sales["State"].map(us_state_abbrev)

fig6 = px.choropleth(
    state_sales,
    locations="State",
    locationmode="USA-states",
    color="Sales",
    scope="usa",
    color_continuous_scale="Viridis",
    template="plotly_white"
)
fig6.update_layout(
    geo=dict(bgcolor='rgba(0,0,0,0)'),
    margin=dict(l=0, r=0, t=0, b=0)
)
st.plotly_chart(fig6, use_container_width=True)


st.markdown("---")

# Top 10 Customers by Sales
st.subheader("Top 10 Customers by Sales")
customer_sales = filtered_df.groupby("Customer Name")["Sales"].sum().nlargest(10).reset_index()
fig7 = px.bar(customer_sales, x="Customer Name", y="Sales", template="seaborn")
st.plotly_chart(fig7, use_container_width=True)

st.markdown("---")

# Sales by Shipping Mode
st.subheader("Sales by Shipping Mode")
shipping_sales = filtered_df.groupby("Ship Mode")["Sales"].sum().reset_index()
fig8 = px.pie(shipping_sales, values="Sales", names="Ship Mode", template="plotly_dark")
st.plotly_chart(fig8, use_container_width=True)

st.markdown("---")

# Profit Margin by Category
st.subheader("Profit Margin by Category")
category_profit_margin = filtered_df.groupby("Category").apply(lambda x: (x["Profit"].sum() / x["Sales"].sum()) * 100).reset_index(name="Profit Margin (%)")
fig9 = px.bar(category_profit_margin, x="Category", y="Profit Margin (%)", template="plotly_white")
st.plotly_chart(fig9, use_container_width=True)

# Download original DataSet
csv = df.to_csv(index=False).encode('utf-8')
st.download_button('Download Data', data=csv, file_name="Data.csv", mime='text/csv')
