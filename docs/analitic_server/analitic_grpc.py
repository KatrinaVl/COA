from proto import analitic_service_pb2
from proto import analitic_service_pb2_grpc
import uuid
from datetime import datetime, date

import json
from google.protobuf import empty_pb2
import grpc

from pydantic import BaseModel
import json
import os

from clickhouse_client import get_likes, get_see, get_comments, get_see_dynamics
from clickhouse_client import get_likes_dynamics, get_comments_dynamics, get_top_posts, get_top_users

from google.protobuf.timestamp_pb2 import Timestamp


class AnaliticServiceImpl(analitic_service_pb2_grpc.AnaliticServiceServicer):

    def GetNumberLikes(self, request, context):

        likes = get_likes(request.id)

        return analitic_service_pb2.Number(
            num=likes
        )

    def GetNumberSee(self, request, context):

        see = get_see(request.id)

        return analitic_service_pb2.Number(
            num=see
        )

    def GetNumberComments(self, request, context):

        comm = get_comments(request.id)

        return analitic_service_pb2.Number(
            num=comm
        )

    def GetSee(self, request, context):
        rows = get_see_dynamics(request.id)
        # items = [
        #     analitic_service_pb2.Day(date=str(row['day']), num=row['views'])
        #     for row in rows
        # ]
        # return analitic_service_pb2.InfoDays(items=items)

        days = []
        for r in rows:
            date_str = r['day']
            num = r['views']

            # dt = datetime.strptime(date_str, '%Y-%m-%d')
            if isinstance(date_str, date):
                dt = datetime.combine(date_str, datetime.min.time())
            else:
                dt = datetime.strptime(date_str, '%Y-%m-%d')

            ts = Timestamp()
            ts.FromDatetime(dt)

            day = analitic_service_pb2.Day(date=ts, num=num)
            days.append(day)

        return analitic_service_pb2.InfoDays(days=days)

    def GetLikes(self, request, context):
        rows = get_likes_dynamics(request.id)
        # items = [
        #     analitic_service_pb2.Day(date=str(row['day']), num=row['likes'])
        #     for row in rows
        # ]
        # return analitic_service_pb2.InfoDays(items=items)

        days = []
        for r in rows:
            date_str = r['day']
            num = r['likes']

            # dt = datetime.strptime(date_str, '%Y-%m-%d')
            if isinstance(date_str, date):
                dt = datetime.combine(date_str, datetime.min.time())
            else:
                dt = datetime.strptime(date_str, '%Y-%m-%d')

            ts = Timestamp()
            ts.FromDatetime(dt)

            day = analitic_service_pb2.Day(date=ts, num=num)
            days.append(day)

        return analitic_service_pb2.InfoDays(days=days)

    def GetComments(self, request, context):
        rows = get_comments_dynamics(request.id)
        # items = [
        #     analitic_service_pb2.Day(date=str(row['day']), num=row['comments'])
        #     for row in rows
        # ]
        # return analitic_service_pb2.InfoDays(items=items)

        days = []
        for r in rows:
            date_str = r['day']
            num = r['comments']

            # dt = datetime.strptime(date_str, '%Y-%m-%d')
            if isinstance(date_str, date):
                dt = datetime.combine(date_str, datetime.min.time())
            else:
                dt = datetime.strptime(date_str, '%Y-%m-%d')

            ts = Timestamp()
            ts.FromDatetime(dt)

            day = analitic_service_pb2.Day(date=ts, num=num)
            days.append(day)

        return analitic_service_pb2.InfoDays(days=days)

    def GetTopPosts(self, request, context):
        rows = get_top_posts(request.type)
        items = [
            analitic_service_pb2.Id(id=row['post_id'], count=row['count'])
            for row in rows
        ]
        return analitic_service_pb2.IDs(ids=items)

    def GetTopUsers(self, request, context):
        rows = get_top_users(request.type)
        items = [
            analitic_service_pb2.Id(id=row['user_id'], count=row['count'])
            for row in rows
        ]
        return analitic_service_pb2.IDs(ids=items)

    
