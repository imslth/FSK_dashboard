import json
import math
import time
import pandas as pd
import requests
import streamlit as st
import datetime
import plotly.graph_objects as go

st.set_page_config(layout="wide")


theme_id = st.secrets.theme_id
api_key_br = st.secrets.api_key_br
api_key_tgstat = st.secrets.api_key_tgstat


def main():
    st.title('Состояние информационного поля компании ГК ФСК')

    st.header('Новые публикации в информационном поле (на базе источника https://brandanalytics.ru/)')

    today = datetime.datetime.now()
    choose_date = st.date_input(
        "Выберете период для получения данных",
        (datetime.date(today.year, today.month, today.day - 10), datetime.date(today.year, today.month, today.day)),

    )

    time_in = time.mktime(choose_date[0].timetuple())

    try:
        time_out = time.mktime(choose_date[1].timetuple())
    except:
        st.error('Укажите диапазон дат')
        st.stop()

    frontend_brand(time_in=time_in, time_out=time_out)
    frontend_top()
    frontend_tgstat()


def frontend_brand(time_in: str, time_out: str) -> None:
    data = brand(method='tonality', time_in=time_in, time_out=time_out)

    all_messages = {
        'count previous': data['data']['previous']['msgs'],
        'count current': data['data']['current']['msgs'],
        'tone previous':
            {
                'позитивные упоминания': data['data']['previous']['tone']['absolute']['positive'],
                'нейтральные упоминания': data['data']['previous']['tone']['absolute']['neutral'],
                'негативные упоминания': data['data']['previous']['tone']['absolute']['negative']
            },
        'tone current':
            {
                'позитивные упоминания': data['data']['current']['tone']['absolute']['positive'],
                'нейтральные упоминания': data['data']['current']['tone']['absolute']['neutral'],
                'негативные упоминания': data['data']['current']['tone']['absolute']['negative']
            }
    }

    date, pos, neu, neg = [], [], [], []

    for item in data['data']['current']['histogram']:
        date.append(datetime.datetime.utcfromtimestamp(int(item)).strftime('%Y-%m-%d'))
        pos.append(data['data']['current']['histogram'][item]['tone']['positive'])
        neu.append(data['data']['current']['histogram'][item]['tone']['neutral'])
        neg.append(data['data']['current']['histogram'][item]['tone']['negative'])

    graphs_list = [
        {
            'x': date,
            'y': pos,
            'name': "Позитивные упоминания",
            'color': 'green'
        },
        {
            'x': date,
            'y': neu,
            'name': "Нейтральные упоминания",
            'color': 'blue'
        }, {
            'x': date,
            'y': neg,
            'name': "Негативные упоминания",
            'color': 'red'
        },
    ]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Всего упоминаний", all_messages['count current'],
                all_messages['count current'] - all_messages['count previous'])
    col2.metric("Позитивных упоминаний", all_messages['tone current']['позитивные упоминания'],
                all_messages['tone current']['позитивные упоминания'] - all_messages['tone previous'][
                    'позитивные упоминания'])
    col3.metric("Нейтральных упоминаний", all_messages['tone current']['нейтральные упоминания'],
                all_messages['tone current']['нейтральные упоминания'] - all_messages['tone previous'][
                    'нейтральные упоминания'])
    col4.metric("Негативных упоминаний", all_messages['tone current']['негативные упоминания'],
                all_messages['tone current']['негативные упоминания'] - all_messages['tone previous'][
                    'негативные упоминания'])

    col1, col2 = st.columns(2)

    with col1:
        labels = list(all_messages['tone current'].keys())
        values = list(all_messages['tone current'].values())
        pie_graphs(x=labels, y=values, title='Распределение сообщений по тональности')

    with col2:
        few_line_graphs(data=graphs_list, title='Динамика публикации сообщений по тональности',
                        ytitle='Количество упоминаний')

    #
    # data = brand('hubtypes',time_in,time_out)
    #
    # labels, values = [], []
    #
    # for item in data['data']['hubtypes']:
    #     labels.append(item['hubtypeName'])
    #     values.append(item['msgs'])
    #
    #
    # col1, col2= st.columns(2)
    #
    # with col1:
    #     choose_channel = st.selectbox('Выберете источник', labels)
    #
    #     date, pos, neu, neg = [], [], [], []
    #
    #     for item in data['data']['hubtypes']:
    #         if item['hubtypeName'] == choose_channel:
    #             for key, value in item['histogram'].items():
    #                 date.append(datetime.datetime.utcfromtimestamp(int(key)).strftime('%Y-%m-%d'))
    #                 pos.append(value['tone']['positive'])
    #                 neu.append(value['tone']['neutral'])
    #                 neg.append(value['tone']['negative'])
    #
    #     fig = go.Figure()
    #     fig.add_trace(go.Scatter(x=date, y=pos, name="Позитивные упоминания",line=dict(color='green', width=4)))
    #     fig.add_trace(go.Scatter(x=date, y=neg, name="Негативные упоминания",line=dict(color='red', width=4)))
    #     fig.add_trace(go.Scatter(x=date, y=neu, name="Нейтральные упоминания",line=dict(color='blue', width=4)))
    #
    #     fig.update_traces(mode='lines+markers', hovertemplate="%{y}%{_xother}")
    #
    #     fig.update_layout(legend=dict(y=0.5, traceorder='reversed', font_size=16),
    #                       title_text='Динамика публикации сообщений по тональности',
    #                       xaxis_title='Дата',
    #                       yaxis_title='Количество упоминаний')
    #
    #     st.plotly_chart(fig, use_container_width=True)
    #
    #
    #
    # with col2:
    #     fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.3)])
    #     fig.update_layout(title_text='Распределение сообщений по источникам')
    #     st.plotly_chart(fig, use_container_width=True)

    # col1, col2= st.columns(2)
    #
    # with col1:

    size = st.slider('Количество тэгов', 0, 20, 5)

    data = brand(method='toptags', time_in=time_in, time_out=time_out, size=size)

    labels, values = [], []
    tag_id = {}

    for item in data['data']['top_tags']:
        labels.append(item['top_tags'])
        values.append(item['msgs'])
        tag_id[item['top_tags']] = item['tag_id']

    bar_graphs(x=labels, y=values, title='Распределение сообщений по тегам')

    #
    # with col2:
    #
    #     choose_tag = st.selectbox('Выберете тэг', tag_id.keys())
    #
    #     data = brand('tagsstat', time_in, time_out, tag=tag_id[choose_tag])
    #
    #     date, pos, neu, neg = [], [], [], []
    #
    #     for item in data['data']['tags']['current']['tags'].values():
    #         for key, value in item['histogram'].items():
    #                 date.append(datetime.datetime.utcfromtimestamp(int(key)).strftime('%Y-%m-%d'))
    #                 pos.append(value['tone']['positive'])
    #                 neu.append(value['tone']['neutral'])
    #                 neg.append(value['tone']['negative'])
    #
    #     fig = go.Figure()
    #     fig.add_trace(go.Scatter(x=date, y=pos, name="Позитивные упоминания",line=dict(color='green', width=4)))
    #     fig.add_trace(go.Scatter(x=date, y=neg, name="Негативные упоминания",line=dict(color='red', width=4)))
    #     fig.add_trace(go.Scatter(x=date, y=neu, name="Нейтральные упоминания",line=dict(color='blue', width=4)))
    #
    #     fig.update_traces(mode='lines+markers', hovertemplate="%{y}%{_xother}")
    #
    #     fig.update_layout(legend=dict(y=0.5, traceorder='reversed', font_size=16),
    #                       title_text='Динамика публикации сообщений по тэгам',
    #                       xaxis_title='Дата',
    #                       yaxis_title='Количество упоминаний')
    #
    #     st.plotly_chart(fig, use_container_width=True)


def frontend_top():
    st.header('Поисковая выдача объектов компании ГК ФСК')

    df = read_excel()

    col1, col2 = st.columns(2)
    # with col1:
    #     labels = list(df.types.value_counts().to_dict().keys())
    #     values = list(df.types.value_counts().to_dict().values())
    #
    #     fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.3)])
    #     fig.update_layout(title_text='Распределение площадок из ТОП выдачи по типам')
    #     st.plotly_chart(fig, use_container_width=True)
    with col1:
        labels = list(df.tone.value_counts().to_dict().keys())
        values = list(df.tone.value_counts().to_dict().values())

        pie_graphs(x=labels, y=values, title='Распределение площадок из ТОП выдачи по тональности')

    with col2:
        rating = []
        for mounth in df.mounth.unique():
            rating.append(df[df.mounth == mounth].rating.mean())

        line_graphs(x=df.mounth.unique(), y=rating, name="Средний рейтинг",
                    title='Динамика изменения среднего рейтинга на площадках',
                    ytitle='Средний рейтинг')

    col1, col2, col3 = st.columns(3)
    project = col1.selectbox('Выбор проекта', df.project.unique())

    dict_df = {}

    for mounth in df.mounth.unique():
        dict_df[mounth] = df[(df.project == project) & (df.mounth == mounth)].types.value_counts().to_dict()

    i = 0
    cols = st.columns(len(dict_df[list(dict_df.keys())[-1]]))
    for key, value in dict_df[list(dict_df.keys())[-1]].items():
        try:
            cols[i].metric(key, value, value - dict_df[list(dict_df.keys())[-2]][key])
            i += 1
        except:
            break

    col1, col2 = st.columns(2)

    with col1:
        pos, neu, neg, without = [], [], [], []
        for mounth in df.mounth.unique():
            try:
                pos.append(df[(df.project == project) & (df.mounth == mounth)].tone.value_counts().to_dict()[
                        'положительная тональность'])
            except:
                pass
            try:
                neu.append(df[(df.project == project) & (df.mounth == mounth)].tone.value_counts().to_dict()[
                        'нейтральная тональность'])
            except:
                pass
            try:
                neg.append(df[(df.project == project) & (df.mounth == mounth)].tone.value_counts().to_dict()[
                        'негативная тональность'])
            except:
                pass
            try:
                without.append(df[(df.project == project) & (df.mounth == mounth)].tone.value_counts().to_dict()[
                        'тональность отсутствует'])
            except:
                pass

        graphs_list = [
            {
                'x': df[df.project == project].mounth.unique(),
                'y': pos,
                'name': "Позитивная тональность",
                'color': 'green'
            },
            {
                'x': df[df.project == project].mounth.unique(),
                'y': neu,
                'name': "Нейтральная тональность",
                'color': 'blue'
            },
            {
                'x': df[df.project == project].mounth.unique(),
                'y': neg,
                'name': "Негативная тональность",
                'color': 'red'
            },
            {
                'x': df[df.project == project].mounth.unique(),
                'y': without,
                'name': "Без тональности",
                'color': 'gray'
            },
        ]

        few_bar_graphs(data=graphs_list, title='Динамика изменения тональности площадок из ТОП выдачи')

    with col2:
        rating = []
        for mounth in df.mounth.unique():
            rating.append(df[(df.project == project) & (df.mounth == mounth)].rating.mean())
        line_graphs(x=df.mounth.unique(), y=rating, name="Средний рейтинг",
                    title='Динамика изменения среднего рейтинга проекта на площадках', ytitle='Средний рейтинг')


def frontend_tgstat():
    st.header('Упоминания компании и объектов в мессенджере Telegram')

    choose_search = st.selectbox('Выберете нужный проект', ('ГК ФСК', 'Первый ДСК', 'ЖК Архитектор'))

    if choose_search != st.session_state.choose_search:
        st.session_state.post = 0
        st.session_state.choose_search = choose_search

    data = tgstat(method='new', search=choose_search)

    total_count = data['response']['total_count']

    data_list = []

    for i in range(math.ceil(total_count / 50)):
        data = tgstat('other', choose_search, 50 * i)
        for item in data['response']['items']:
            data_list.append(item)

    st.metric("Всего упоминаний за последние 3 дня", total_count)

    dict_df = {
        'id_post': [item['id'] for item in data_list],
        'date': [datetime.datetime.utcfromtimestamp(int(item['date'])).strftime('%Y-%m-%d') for item in
                 data_list],
        'views': [item['views'] for item in data_list],
        'link': [item['link'] for item in data_list],
        'channel_id': [item['channel_id'] for item in data_list],
        'text': [item['text'] for item in data_list],
        'comments_count': [item['comments_count'] for item in data_list],
        'reactions_count': [item['reactions_count'] for item in data_list],
    }

    df = pd.DataFrame(dict_df)

    count_df = df.groupby('date')['link'].count().to_dict()
    views_df = df.groupby('date')['views'].sum().to_dict()
    comments_count_df = df.groupby('date')['comments_count'].sum().to_dict()
    reactions_count_df = df.groupby('date')['reactions_count'].sum().to_dict()

    tab1, tab2, tab3, tab4 = st.tabs(["Публикации", "Просмотры", "Реакции", "Комментарии"])

    with tab1:
        line_graphs(x=list(count_df.keys()), y=list(count_df.values()), name="Количество сообщений",
                    title='Динамика публикаций сообщений в мессенджере Telegram', ytitle='Количество сообщений')

    with tab2:
        line_graphs(x=list(views_df.keys()), y=list(views_df.values()), name="Количество просмотров",
                    title='Динамика просмотров сообщений в мессенджере Telegram', ytitle='Количество просмотров')

    with tab3:
        line_graphs(list(reactions_count_df.keys()), list(reactions_count_df.values()), "Количество реакций",
                    'Динамика реакций к сообщениям в мессенджере Telegram', 'Количество реакций')

    with tab4:
        line_graphs(list(comments_count_df.keys()), list(comments_count_df.values()), "Количество комментариев",
                    'Динамика комментариев к сообщениям в мессенджере Telegram', 'Количество комментариев')

    col1, col2 = st.columns([1, 4])

    with col1:
        if st.button('Следующая публикация'): st.session_state.post += 1
        if st.button('Предыдущая публикация'): st.session_state.post -= 1

    with col2:
        with st.expander("Текст публикации"):
            st.markdown(f"🔗 - https://{dict_df['link'][st.session_state.post]}", unsafe_allow_html=True)
            st.markdown(f":calendar: - {dict_df['date'][st.session_state.post]}", unsafe_allow_html=True)
            st.markdown(f"👀 - {dict_df['views'][st.session_state.post]}  просмотров", unsafe_allow_html=True)
            st.markdown(f"💬 - {dict_df['comments_count'][st.session_state.post]}  комментариев", unsafe_allow_html=True)
            st.markdown(f"👍 - {dict_df['reactions_count'][st.session_state.post]}  реакций", unsafe_allow_html=True)
            st.markdown(dict_df['text'][st.session_state.post], unsafe_allow_html=True)


def line_graphs(x: list, y: list, name: str, title: str, ytitle: str) -> None:
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(x=x, y=y, name=name, line=dict(color='gray', width=4)))
    fig.update_traces(mode='lines+markers', hovertemplate="%{y}%{_xother}")
    fig.update_layout(legend=dict(y=0.5, traceorder='reversed', font_size=16),
                      title_text=title,
                      xaxis_title='Дата',
                      yaxis_title=ytitle)
    st.plotly_chart(fig, use_container_width=True)


def pie_graphs(x: list, y: list, title: str) -> None:
    fig = go.Figure(data=[go.Pie(labels=x, values=y, hole=.3, marker_colors=['green', 'blue', 'red'])])
    fig.update_layout(title_text=title)
    st.plotly_chart(fig, use_container_width=True)


def few_line_graphs(data: list, title: str, ytitle: str) -> None:
    fig = go.Figure()
    for item in data:
        fig.add_trace(go.Scatter(x=item['x'], y=item['y'], name=item['name'], line=dict(color=item['color'], width=4)))
    fig.update_traces(mode='lines+markers', hovertemplate="%{y}%{_xother}")
    fig.update_layout(legend=dict(y=0.5, traceorder='reversed', font_size=16),
                      title_text=title,
                      xaxis_title='Дата',
                      yaxis_title=ytitle)
    st.plotly_chart(fig, use_container_width=True)


def bar_graphs(x: list, y: list, title) -> None:
    fig = go.Figure(data=[go.Bar(name='сообщений', x=x, y=y, marker_color='gray', text=y)])
    fig.update_layout(barmode='stack')
    fig.update_layout(title_text=title)
    fig.update_traces(hovertemplate="%{y}%{_xother}")
    st.plotly_chart(fig, use_container_width=True)


def few_bar_graphs(data: list, title: str) -> None:
    fig = go.Figure()
    for item in data:
        fig.add_trace(go.Bar(x=item['x'], y=item['y'], marker_color=item['color'], text=item['y'], name=item['name']))
    fig.update_layout(barmode='stack')
    fig.update_layout(title_text=title)
    fig.update_traces(hovertemplate="%{y}%{_xother}")
    st.plotly_chart(fig, use_container_width=True)


@st.cache_data
def brand(method: str, time_in: str, time_out: str, size=None, tag=None) -> json:
    if method == 'toptags':
        r = requests.get(
            f'https://brandanalytics.ru/v1/statistic/{method}/?themeId={theme_id}&timeFrom={time_in}&timeTo={time_out}&token={api_key_br}&params[size]={size}')
    elif method == 'tagsstat':
        r = requests.get(
            f'https://brandanalytics.ru/v1/statistic/{method}/?themeId={theme_id}&timeFrom={time_in}&timeTo={time_out}&token={api_key_br}&params[tags][]={tag}')
    else:
        r = requests.get(
            f'https://brandanalytics.ru/v1/statistic/{method}/?themeId={theme_id}&timeFrom={time_in}&timeTo={time_out}&token={api_key_br}')
    return r.json()


@st.cache_data
def tgstat(method: str, search: str, n=None) -> json:
    if method == 'new':
        r = requests.get(f'https://api.tgstat.ru/posts/search?token={api_key_tgstat}&q={search}&limit=50')
    else:
        r = requests.get(f'https://api.tgstat.ru/posts/search?token={api_key_tgstat}&q={search}&limit=50&offset={n}')
    return r.json()


@st.cache_data
def read_excel() -> pd.DataFrame:
    df = pd.read_excel('data.xlsx')
    return df


if __name__ == '__main__':
    if 'post' not in st.session_state: st.session_state.post = 0
    if 'choose_search' not in st.session_state: st.session_state.choose_search = ''
    main()
