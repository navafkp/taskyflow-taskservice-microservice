from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import (
    BoardSerializer, CardSerailizer,
    getAllColumnSerializer, getAllCardSerializer,
    getAllAssigneeSerializer, getAllBoardSerializer,
    AssigneeSerailizer, CommentsSerializer,
    GetCommentsSerializer, MeetingSerialzer,
    GetMeetingSerialzer, ColumnSerializer
)
from rest_framework.exceptions import ValidationError, AuthenticationFailed
from .models import Columns, Boards, Assignee, Card, Comments, Meeting
from django.db.models import Q
import jwt, os, smtplib
from django.db import transaction
from rest_framework import serializers
from django.db import IntegrityError
from dotenv import load_dotenv
from .producer import publish_to_notification
from smtplib import SMTPConnectError
from datetime import datetime

# Load the stored environment variables
load_dotenv()

secret_key = os.getenv('SECRET_KEY')
senderEmail = os.getenv('SENDER_EMAIL')
senderPssword = os.getenv('PASSWORD')

def tokenSplit(auth_author):
    """get access token with bearer, spilt and return teh access token"""

    if not auth_author or 'Bearer' not in auth_author:
        raise AuthenticationFailed("Unauthorized User")
    token = auth_author.split('Bearer ')[1]
    return token


def decode_jwt(token):
    """# decoding the access token"""

    try:
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        raise jwt.ExpiredSignatureError("Token has expired")
    except jwt.InvalidSignatureError:
        raise jwt.InvalidSignatureError("Invalid token signature")
    except jwt.DecodeError:
        raise jwt.DecodeError("Error decoding the token")


class BoardAction(APIView):

    def post(self, request):
        """Given details, creating board"""

        try:
            serialize = BoardSerializer(data=request.data)
            serialize.is_valid(raise_exception=True)
            serialize.save()
            border = Boards.objects.filter(
                name=serialize.data['name']
            ).first()
            title_name = ['assigned', 'inprogres', 'completed']

            for i in range(3):
                Columns.objects.create(
                    board_id=border,
                    title=title_name[i],
                    position=i+1
                )
            x = Boards.objects.get(name=serialize.data['name'])
            serilai = getAllBoardSerializer(x)
            board_to_notification = dict(
                content=f"Board has been created with the name {serilai.data['name']}",
                type='Board Creation',
                workspace=serilai.data['workspace'],
            )
            if serilai.data['visibility'] == 'private':
                board_to_notification['category'] = 'personal'
            try:
                publish_to_notification(
                    'new board has been created', board_to_notification)
            except Exception as e:
                print(str(e))

            return Response(serilai.data)
        except ValidationError as e:
            error_message = str(e.detail.get('name', ''))
            if 'unique' in error_message.lower():
                return Response({"error": "Board with this name already exists"}, status=status.HTTP_400_BAD_REQUEST)
            return Response({"error": str(e)})
        except Exception as e:
            return Response({"error": "Something went wrong, try again"})

    def get(self, request):
        """get all boards"""

        auth_author = request.data.get('auth_author')
        workspace = request.data.get('workspace')
        # spliting the auth_author to get access token
        token = tokenSplit(auth_author)
        try:
            payload = decode_jwt(token)  # decoding access token
            workspace_all_board = Boards.objects.filter(
                workspace=workspace).filter(is_active=True)
            serialize = getAllBoardSerializer(workspace_all_board, many=True)
            return Response({"data": serialize.data})

        except Boards.DoesNotExist as e:
            return Response({'error': "there is no board under this workspae"})
        except ValidationError as e:
            return Response({'error': str(e)})
        except Exception as e:
            return Response({"error": "Something went wrong"})


class DeleteBoard(APIView):
    """Given details, deleteing board"""

    def delete(self, request, id=None):
        auth_author = request.headers.get('authorization')
        token = tokenSplit(auth_author)
        try:
            payload = decode_jwt(token)  # decoding access token
            board_obj = Boards.objects.get(id=id)
            board_obj.is_active = False
            board_obj.save()
            return Response({"success": "Board deleted successfully"})
        except Boards.DoesNotExist:
            return Response({"error": "There is no boards with the id"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(str(e))
            return Response({"error": "Something went wrong"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ColumnsAction(APIView):

    def get(self, request):
        """Given details, get all columns"""

        board_slug = request.data.get('board_slug')
        auth_author = request.data.get('auth_author')
        # spliting the auth_author to get access token
        token = tokenSplit(auth_author)
        try:
            payload = decode_jwt(token)  # decoding access token
            board_obj = Boards.objects.get(slug=board_slug)
            if board_obj:
                columns_obj = Columns.objects.filter(
                    board_id=board_obj).order_by('position')
                serialzer = getAllColumnSerializer(columns_obj, many=True)
                return Response(serialzer.data)

        except Boards.DoesNotExist as e:
            return Response({"error": "There is no boards with the name"}, status=status.HTTP_404_NOT_FOUND)
        except Columns.DoesNotExist as e:
            return Response({"error": "There is no columns under this board"}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as e:
            return Response({'error': str(e)})
        except Exception as e:
            return Response({"error": "Something went wrong"})

    def post(self, request):
        """Given details, create a column"""

        board_id = request.data.pop('boardId')
        auth_author = request.headers.get('authorization')
        token = tokenSplit(auth_author)
        try:
            payload = decode_jwt(token)  # decoding access token
            board_obj = Boards.objects.get(id=board_id)
            request.data['board_id'] = board_obj.id
            serializer = ColumnSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        except Boards.DoesNotExist as e:
            print(str(e))
            return Response({"error": "Boards not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(str(e))
            return Response({"error": "Something went wrong"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Given details, update column details
    def patch(self, request):
        auth_author = request.headers.get('authorization')
        token = tokenSplit(auth_author)
        try:
            payload = decode_jwt(token)  # decoding access token
            board_id = request.data.get('boardID')
            board_obj = Boards.objects.get(id=board_id)
            column_position = request.data.get('position')
            column_obj = Columns.objects.filter(
                board_id=board_obj, position=column_position).first()
            column_obj.title = request.data.get('title')
            column_obj.save()
            return Response({"success": "column renamed"})

        except Boards.DoesNotExist:
            return Response({"error": "Boards not found"})
        except Columns.DoesNotExist:
            return Response({"error": "Columns not found"})
        except Exception as e:
            print(str(e))
            return Response({"error": "Something went wrong"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CardAction(APIView):

    def post(self, request):
        """Given details, creating card """

        auth_author = request.headers.get('authorization')
        token = tokenSplit(auth_author)
        assignee_details = request.data.pop('assignee', None)
        max_members = request.data.get('max_members', None)
        if max_members == None:
            request.data.pop('max_members', None)
            request.data['max_members'] = 1
        try:
            payload = decode_jwt(token)
            board_id = request.data.pop('board', None)
            if board_id is not None:
                board_obj = Boards.objects.get(id=board_id)
                if board_obj:
                    request.data['board'] = board_obj.id
                    serialize = CardSerailizer(data=request.data)
                    serialize.is_valid(raise_exception=True)
                    serialize.save()
                    if assignee_details is not None:
                        try:
                            card = Card.objects.get(
                                id=serialize.data['id']
                            )
                            for email in assignee_details:
                                try:
                                    Assignee.objects.create(
                                        card=card, user=email
                                    )
                                    message = f"You have been added to the card titled '{serialize.data['title']}' on the board '{board_obj.name}'"
                                    receiver_email = email
                                    sender_email = senderEmail
                                    password = senderPssword
                                    try:
                                        with smtplib.SMTP("smtp.gmail.com", 587) as server:
                                            server.starttls()
                                            server.login(
                                                sender_email, password)
                                            server.sendmail(
                                                sender_email, receiver_email, message)
                                    except SMTPConnectError:
                                        continue
                                    except Exception as e:
                                        print(str(e))
                                        continue

                                    card_to_notification = {
                                        'content': f"Card has been created with the title {serialize.data['title']}",
                                        'type': 'Card Creation',
                                        'workspace': 'None',
                                        'category': 'personal',
                                        'userMail': email
                                    }

                                    try:
                                        publish_to_notification(
                                            'new card has been created', card_to_notification)
                                    except Exception as e:
                                        print(str(e))
                                        continue
                                except Exception as e:
                                    return Response({"error": "Unable to add assigness"})
                            assignee_data = Assignee.objects.filter(
                                card=card).values()
                            new_assignee_data = list(assignee_data.values())
                            seria = getAllAssigneeSerializer(
                                new_assignee_data, many=True)
                            data = {'card': serialize.data,
                                    'assignee': seria.data}
                            return Response(data)
                        except Card.DoesNotExist as e:
                            return Response({"error": "card not found"})
                    else:
                        return Response({'card': serialize.data, 'assignee': None})
            else:
                return Response({"error": "Board ID is required"})

        except ValidationError as e:
            return Response({"error": str(e)})
        except Boards.DoesNotExist as e:
            return Response({"error": "There is no board, please create a board first"})
        except Exception as e:
            print(str(e))
            return Response({"error": "Something went wrong"})

    def get(self, request):
        """Get all cards"""

        board_slug = request.data.get('board_slug')
        auth_author = request.data.get('auth_author')
        # spliting the auth_author to get access token
        token = tokenSplit(auth_author)
        try:
            payload = decode_jwt(token)  # decoding access token
            board_obj = Boards.objects.filter(slug=board_slug).first()
            if board_obj:
                card_obj = Card.objects.filter(board=board_obj)
                assigne_data = []
                for card in card_obj:
                    x = Assignee.objects.filter(card_id=card).values()
                    assigne_data.append(x)
                list_of_dicts = [
                    item for sublist in assigne_data for item in sublist.values()]
                serializerAssignee = getAllAssigneeSerializer(
                    list_of_dicts, many=True)
                serializer = getAllCardSerializer(card_obj, many=True)
                data = {"card": serializer.data,
                        'assignee': serializerAssignee.data}
                return Response(data)

        except Boards.DoesNotExist as e:
            return Response({"error": "There is no boards with the name"}, status=status.HTTP_404_NOT_FOUND)
        except Card.DoesNotExist as e:
            return Response({"error": "There is no card for the columns"}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as e:
            return Response({"error": str(e)})
        except Exception as e:
            print(str(e))
            return Response({"error": "Something went wrong"})

    def patch(self, request):
        """Given details for card dragging, update card"""

        card_id = request.data.get('card_id')
        column_id = request.data.get('column_id')
        auth_author = request.data.get('auth_author')
        # spliting the auth_author to get access token
        token = tokenSplit(auth_author)
        try:
            payload = decode_jwt(token)  # decoding access token
            card_obj = Card.objects.get(id=card_id)
            if card_obj:
                card_obj.column = column_id
                card_obj.save()
                serializer = getAllCardSerializer(card_obj)
                return Response(serializer.data)
        except Card.DoesNotExist as e:
            return Response({"error": "There is no card for the columns"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": "Something went wrong"})


class CardEditUpdate(APIView):
    """Given details, update card details"""

    def patch(self, request):
        card_id = request.data.get('cardId')
        card_data = request.data.get('updatedData')
        auth_author = request.headers.get('authorization')
        token = tokenSplit(auth_author)
        try:
            payload = decode_jwt(token)  # decoding access token
            card_obj = Card.objects.get(id=card_id)

            for key, value in card_data.items():
                setattr(card_obj, key, value)

            with transaction.atomic():
                card_obj.save()

            return Response({'message': 'Card updated successfully'})
        except Card.DoesNotExist as e:
            print(str(e))
            return Response({"error": "Crad not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(str(e))
            return Response({"error": "Something went wrong"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CardDeletion(APIView):
    """Given details, delete card"""

    def delete(self, request, id=None):
        auth_author = request.data.get('auth_author')
        # spliting the auth_author to get access token
        token = tokenSplit(auth_author)

        try:
            payload = decode_jwt(token)  # decoding access token
            card_obj = Card.objects.get(id=id)
            card_obj.delete()
            return Response({"success": "The card has been deleted Succesfully"})
        except Card.DoesNotExist as e:
            return Response({"error": "There is no card with the card id"})
        except Exception as e:
            print(str(e))
            return Response({"error": "Something went wrong"})


class AddAssignee(APIView):
    """Given details, create assignee"""

    def post(self, request):
        card_id = request.data.get('card_id')
        user_emails = request.data.get('selectedEmails')
        auth_author = request.headers.get('authorization')
        token = tokenSplit(auth_author)
        try:
            payload = decode_jwt(token)  # decoding access token
            card_obj = Card.objects.select_related('board').get(id=card_id)
            board_name = card_obj.board.name
            new_assignee_data = []
            for user in user_emails:
                card_data = {'user': user, 'card': card_obj.id}
                serialize = AssigneeSerailizer(data=card_data)
                for email in user_emails:
                    assignee_card_to_notification = {
                        'content': f"You have been assigned to a card '{card_obj.title}'",
                        'type': 'Assigned to Card',
                        'workspace': 'None',
                        'category': 'personal',
                        'userMail': email
                    }
                    try:
                        publish_to_notification(
                            'new card has been created to you', assignee_card_to_notification)
                    except Exception as e:
                        print(str(e))
                        continue
                try:
                    serialize.is_valid(raise_exception=True)
                    serialize.save()
                    message = f"You have been added to the card titled '{card_obj.title}' on the board '{board_name}'"
                    receiver_email = serialize.data['user']
                    sender_email = senderEmail
                    password = senderPssword
                    try:
                        with smtplib.SMTP("smtp.gmail.com", 587) as server:
                            server.starttls()
                            server.login(sender_email, password)
                            server.sendmail(
                                sender_email, receiver_email, message)
                    except SMTPConnectError:
                        continue
                    except Exception as e:
                        print(str(e))
                        continue
                    new_assignee_data.append(serialize.data)
                except serializers.ValidationError as validation_error:
                    print(f"ValidationError: {validation_error}")
                    error_message = str(e.detail.get('non_field_errors', ''))
                    if 'unique' in error_message.lower():
                        return Response({"error": "Member with this name already exists"}, status=status.HTTP_400_BAD_REQUEST)

                except IntegrityError as integrity_error:
                    # Handle the unique constraint violation error
                    print(f"IntegrityError: {integrity_error}")
                    continue
            return Response(new_assignee_data)
        except Card.DoesNotExist:
            return Response({"error": "Card not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": "Something went wrong"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AssigneeDeleteion(APIView):
    """Given details, delete assignees"""

    def delete(self, request, id=None):
        auth_author = request.data.get('auth_author')
        # spliting the auth_author to get access token
        token = tokenSplit(auth_author)

        try:
            payload = decode_jwt(token)  # decoding access token
            assignee = Assignee.objects.get(id=id)
            assignee.delete()
            return Response("Successfully deleted")
        except Assignee.DoesNotExist:
            return Response({"error": "Assignee not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(str(e))
            return Response({"error": "Something went wrong"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CommentAction(APIView):
    """Given details, create comment for card"""

    def post(self, request, id=None):
        auth_author = request.headers.get('authorization')
        token = tokenSplit(auth_author)
        try:
            payload = decode_jwt(token)  # decoding access token
            card_id = request.data.pop('card_id')
            card_obj = Card.objects.get(id=card_id)
            request.data['card'] = card_obj.id
            serialize = CommentsSerializer(data=request.data)
            serialize.is_valid(raise_exception=True)
            serialize.save()
            return Response(serialize.data)

        except Exception as e:
            print(str(e))
            return Response({"error": "Something went wrong"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GetComments(APIView):
    """Given details, get the comments details"""

    def get(self, request):
        card_id = request.data.get('card_id')
        auth_author = request.headers.get('authorization')
        token = tokenSplit(auth_author)
        try:
            payload = decode_jwt(token)  # decoding access token
            card_obj = Card.objects.get(id=card_id)
            comment_obj = Comments.objects.filter(
                card=card_obj.id).order_by('-created_at')
            serializer = GetCommentsSerializer(comment_obj, many=True)
            return Response(serializer.data)
        except Card.DoesNotExist as e:
            print(str(e))
            return Response({"error": "Crad not found"}, status=status.HTTP_404_NOT_FOUND)
        except Comments.DoesNotExist as e:
            print(str(e))
            return Response({"error": "Comments not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(str(e))
            return Response({"error": "Something went wrong"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CreateMeeting(APIView):
    """Given details, create meeting"""

    def post(self, request):
        meeting_details = request.data
        date_time_str = request.data.get('starting_time')
        roomID = request.data.pop('roomID')
        removeSpace_roomID = roomID.replace(" ", "")
        request.data['roomID'] = removeSpace_roomID
        duration = int(request.data.pop('duration'))
        expiration_time = int(date_time_str) + (duration * 60)
        request.data['expiration_time'] = expiration_time
        serializer = MeetingSerialzer(data=meeting_details)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class MeetingAction(APIView):
    """Given details, get the meeting details"""

    def get(self, request):
        workspace = request.data.get('workspace')
        auth_author = request.headers.get('authorization')
        # spliting the auth_author to get access token
        token = tokenSplit(auth_author)

        if token:
            payload = decode_jwt(token)  # decoding access token
            try:
                now = datetime.now()
                timestamp = datetime.timestamp(now)
                meeting_data = Meeting.objects.filter(
                    workspace=workspace,
                    expiration_time__gt=timestamp,
                ).filter(is_active=True)

                serialize = GetMeetingSerialzer(meeting_data, many=True)
                return Response(serialize.data)
            except Meeting.DoesNotExist:
                return Response({"error": "Meetings doesnot exists under this workspace"})
        else:
            return Response({"error": 'Unauthorized Access, Token required'})


class DeleteMeeting(APIView):
    """Given details, delete(inactive) the meeting """

    def delete(self, request, id=None):
        auth_author = request.headers.get('authorization')
        # spliting the auth_author to get access token
        token = tokenSplit(auth_author)
        if token:
            try:
                payload = decode_jwt(token)  # decoding access token
                meeting_obj = Meeting.objects.get(id=id)
                meeting_obj.is_active = False
                meeting_obj.save()
                return Response({"success": "Meeting has been deleted"})
            except Meeting.DoesNotExist:
                return Response({"error": "Meetings doesnot exists under this workspace"})
        else:
            return Response({"error": 'Unauthorized Access, Token required'})