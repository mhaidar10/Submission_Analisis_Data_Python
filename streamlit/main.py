import streamlit as st 
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from datetime import datetime
import datetime as dt

all_df = pd.read_csv('all_data.csv')



# change type str/obj -> datetime
datetime_columns = ["order_approved_at"]
for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])

def number_order_per_month(df):
    monthly_df = df.resample(rule='M', on='order_approved_at').agg({
        "order_id": "size",
    })
    monthly_df.index = monthly_df.index.strftime('%B') #mengubah format order_approved_at menjadi Tahun-Bulan
    monthly_df = monthly_df.reset_index()
    monthly_df.rename(columns={
        "order_id": "order_count",
    }, inplace=True)
    monthly_df = monthly_df.sort_values('order_count').drop_duplicates('order_approved_at', keep='last')
    month_mapping = {
        "January": 1,
        "February": 2,
        "March": 3,
        "April": 4,
        "May": 5,
        "June": 6,
        "July": 7,
        "August": 8,
        "September": 9,
        "October": 10,
        "November": 11,
        "December": 12
    }

    monthly_df["month_numeric"] = monthly_df["order_approved_at"].map(month_mapping)
    monthly_df = monthly_df.sort_values("month_numeric")
    monthly_df = monthly_df.drop("month_numeric", axis=1)
    return monthly_df

def customer_spend_df(df):
    sum_spend_df = df.resample(rule='M', on='order_approved_at').agg({
            "price": "sum"
    })
    sum_spend_df = sum_spend_df.reset_index()
    sum_spend_df.rename(columns={
                "price": "total_spend"
            }, inplace=True)
    sum_spend_df['order_approved_at'] = sum_spend_df['order_approved_at'].dt.strftime('%B') 
    sum_spend_df = sum_spend_df.sort_values('total_spend').drop_duplicates('order_approved_at', keep='last')
    custom_order = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

    # Create a categorical column based on the custom order
    sum_spend_df['month_cat'] = pd.Categorical(sum_spend_df['order_approved_at'], categories=custom_order, ordered=True)

    # Sort the DataFrame based on the categorical column
    sorted_df = sum_spend_df.sort_values(by='month_cat')

    # Remove the 'month_cat' column if you don't need it
    sorted_df = sorted_df.drop(columns=['month_cat'])
    return sorted_df


def create_by_product_df(df):
    product_id_counts = df.groupby('product_category_name_english')['product_id'].count().reset_index()
    sorted_df = product_id_counts.sort_values(by='product_id', ascending=False)
    return sorted_df

def rating_cust_df(df):
    rating_service = df['review_score'].value_counts().sort_values(ascending=False)
    
    max_score = rating_service.idxmax()

    df_cust=df['review_score']

    return (rating_service,max_score,df_cust)

def create_rfm(df):
    now=dt.datetime(2018,10,20)



    #alternate code 1
    #df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
    #rfm = df.groupby('customer_id',as_index=False).agg({
    #    'order_purchase_timestamp' : lambda x : (now - x.max()).days,
    #    'order_id': lambda x : len(x),
    #    'price': lambda x : x.sum() 
    #}) 

    #alternate code 2
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
    # Group by 'customer_id' and calculate Recency, Frequency, and Monetary
    recency = (now - df.groupby('customer_id')['order_purchase_timestamp'].max()).dt.days
    frequency = df.groupby('customer_id')['order_id'].count()
    monetary = df.groupby('customer_id')['price'].sum()

    # Create a new DataFrame with the calculated metrics
    rfm = pd.DataFrame({
        'customer_id': recency.index,
        'Recency': recency.values,
        'Frequency': frequency.values,
        'Monetary': monetary.values
    })
    #End alternative 2

    col_list = ['customer_id','Recency','Frequency','Monetary']
    rfm.columns = col_list
    return rfm


# ========================================================================================
# ======================================== SideBar =======================================
# ========================================================================================

with st.sidebar:
    
    # Menambahkan logo perusahaan
    st.image("https://upload.wikimedia.org/wikipedia/commons/7/77/Streamlit-logo-primary-colormark-darktext.png")
    st.write('Copyright (C) © 2023 by Haidar ')
    # Define the URL and link text
    url = "https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce"
    link_text = "Visit Kaggle Dataset "

    # Create the link
    st.write('Brazilian E-Commerce Public Dataset')
    st.write(f"[{link_text}]({url})")
    
    


# calling functions
daily_orders_df=number_order_per_month(all_df)
most_and_least_products_df=create_by_product_df(all_df)
rating_service,max_score,df_rating_service=rating_cust_df(all_df)
customer_spend_df=customer_spend_df(all_df)
rfm=create_rfm(all_df)

# ========================================================================================
# ======================================== Header ========================================
# ========================================================================================

st.header('Brazilian E-Commerce Public Dataset :sparkles:')

# ========================================================================================
# ====================================== Sub Header ======================================
# ========================================================================================


# ========================================================================================
# ================================= Section Month Order ==================================
# ========================================================================================
st.subheader('Monthly Orders')
col1, col2 = st.columns(2)

with col1:
    high_order_num = daily_orders_df['order_count'].max()
    high_order_month=daily_orders_df[daily_orders_df['order_count'] == daily_orders_df['order_count'].max()]['order_approved_at'].values[0]
    st.markdown(f"Highest orders in {high_order_month} : **{high_order_num}**")

with col2:
    low_order = daily_orders_df['order_count'].min()
    low_order_month=daily_orders_df[daily_orders_df['order_count'] == daily_orders_df['order_count'].min()]['order_approved_at'].values[0]
    st.markdown(f"Lowest orders in {low_order_month} : **{low_order}**")

fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    daily_orders_df["order_approved_at"],
    daily_orders_df["order_count"],
    marker='o',
    linewidth=2,
    color="#90CAF9",
)
plt.xticks(rotation=45)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)

st.pyplot(fig)

# ========================================================================================
# =============================== Section Customer Spend =================================
# ========================================================================================
st.subheader('Customer Spend')
col1, col2 = st.columns(2)

with col1:
    total_spend=customer_spend_df['total_spend'].sum()
    formatted_total_spend = "%.2f" % total_spend
    st.markdown(f"Total Spend : **{formatted_total_spend}**")

with col2:
    avg_spend=customer_spend_df['total_spend'].mean()
    formatted_avg_spend = "%.2f" % avg_spend
    st.markdown(f"Average Spend : **{formatted_avg_spend}**")

plt.figure(figsize=(16, 8))
min_total_spend = customer_spend_df['total_spend'].min()
max_total_spend = customer_spend_df['total_spend'].max()

plt.axhline(y=max_total_spend, color='green', linestyle='-', linewidth=0.5, label=f'Max ({max_total_spend:.2f})')
plt.axhline(y=min_total_spend, color='red', linestyle='-', linewidth=0.5, label=f'Min ({min_total_spend:.2f})')
sns.barplot(
    x='order_approved_at',
    y='total_spend',
    data=customer_spend_df,
    #marker='o', 
    #linewidth=2,
    linestyle='-',
    color="#90CAF9",
    
)
plt.xlabel('')
plt.ylabel('Total Spend')
plt.xticks(fontsize=10, rotation=25)
plt.yticks(fontsize=10)
plt.legend()
st.pyplot(plt)

# ========================================================================================
# ================================ Most & Least Products =================================
# ========================================================================================

st.subheader("Most And Least Product")
col1, col2 = st.columns(2)

with col1:
    highest_product_sold=most_and_least_products_df['product_id'].max()
    st.markdown(f"Higest Number : **{highest_product_sold}**")

with col2:
    lowest_product_sold=most_and_least_products_df['product_id'].min()
    st.markdown(f"Lowest Number : **{lowest_product_sold}**")

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(16, 8))

colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

#sns.barplot(x="product_id", y="product_category_name_english", data=most_and_least_products_df.head(5),hue="product_category_name_english", palette=colors, ax=ax[0],)


sns.barplot(
    x="product_id", 
    y="product_category_name_english", 
    data=most_and_least_products_df.head(5), 
    palette=colors, 
    ax=ax[0],
    )
ax[0].set_ylabel('')
ax[0].set_xlabel('')
ax[0].set_title("products with the highest sales", loc="center", fontsize=18)
ax[0].tick_params(axis ='y', labelsize=15)

sns.barplot(
    x="product_id", 
    y="product_category_name_english", 
    data=most_and_least_products_df.sort_values(by="product_id", ascending=True).head(5), 
    palette=colors, 
    ax=ax[1],)
ax[1].set_ylabel('')
ax[1].set_xlabel('')
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("products with the lowest sales", loc="center", fontsize=18)
ax[1].tick_params(axis='y', labelsize=15)

plt.suptitle("most and least sold products", fontsize=20)
st.pyplot(fig)

# ========================================================================================
# ============================= Rating Customer By Service ===============================
# ========================================================================================
st.subheader("Rating Customer By Service")
st.markdown(f"Rating Average  : **{df_rating_service.mean():.2f}**")
    


plt.figure(figsize=(16, 8))
sns.barplot(
            x=rating_service.index, 
            y=rating_service.values, 
            order=rating_service.index,
            palette=["#90CAF9" if score == max_score else "#D3D3D3" for score in rating_service.index],
            #palette=["#90CAF9"]
            
            )

plt.title("Rating customers for service", fontsize=15)
plt.xlabel("Rating")
plt.ylabel("Customer")
plt.xticks(fontsize=12)
st.pyplot(plt)

# ========================================================================================
# ======================================== RFM ===========================================
# ========================================================================================
st.subheader("RFM Best Value")


colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

# beri comentar pada ax[index].set_xticks([]) bila ingin melihat customer nya by id

######################################3
tab1, tab2, tab3 = st.tabs(["Recency", "Frequency", "Monetary"])

with tab1:
    plt.figure(figsize=(16, 8))
    sns.barplot(
        y="Recency", 
        x="customer_id", 
        data=rfm.sort_values(by="Recency", ascending=True).head(5), 
        palette=colors,
        
        )
    plt.title("By Recency (Day)", loc="center", fontsize=18)
    plt.ylabel('')
    plt.xlabel("customer")
    plt.tick_params(axis ='x', labelsize=15)
    plt.xticks([])
    st.pyplot(plt)

with tab2:
    plt.figure(figsize=(16, 8))
    sns.barplot(
        y="Frequency", 
        x="customer_id", 
        data=rfm.sort_values(by="Frequency", ascending=False).head(5), 
        palette=colors,
        
        )
    plt.ylabel('')
    plt.xlabel("customer")
    plt.title("By Frequency", loc="center", fontsize=18)
    plt.tick_params(axis ='x', labelsize=15)
    plt.xticks([])
    st.pyplot(plt)

with tab3:
    plt.figure(figsize=(16, 8))
    sns.barplot(
        y="Monetary", 
        x="customer_id", 
        data=rfm.sort_values(by="Monetary", ascending=False).head(5), 
        palette=colors,
        )
    plt.ylabel('')
    plt.xlabel("customer")
    plt.title("By Monetary", loc="center", fontsize=18)
    plt.tick_params(axis ='x', labelsize=15)
    plt.xticks([])
    st.pyplot(plt)

