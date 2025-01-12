from rest_framework.decorators import api_view , permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import DNAAnalysis
from .serializers import DNAAnalysisSerializer , UserSerializer
from .utils import (
    reverse_complement, visualize_gc_content_graph, translate_sequence,
    detect_mutations, validate_sequence, interactive_gc_content_graph,
    generate_pdf_report, gc_content
)
from django.http import FileResponse

# Reverse Complement View
@swagger_auto_schema(
    method='post',
    operation_summary="Reverse Complement of DNA Sequence",
    operation_description="Generates the reverse complement of a given DNA sequence.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "sequence": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="DNA sequence (string of A, T, C, G)"
            )
        },
        required=["sequence"]
    ),
    responses={
        200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "reverse_complement": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="The reverse complement of the input sequence"
                )
            }
        ),
        400: "Invalid input"
    }
)
@api_view(["POST"])
def reverse_complement_view(request):
    sequence = request.data.get("sequence", "")
    if not sequence:
        return Response({"error": "DNA sequence is required."}, status=status.HTTP_400_BAD_REQUEST)
    try:
        rev_comp_sequence = reverse_complement(sequence)
        return Response({"reverse_complement": rev_comp_sequence}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# GC Content Graph View
@swagger_auto_schema(
    method='post',
    operation_summary="Visualize GC Content Graph",
    operation_description="Generates a graph showing the GC content distribution of the given DNA sequence.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "sequence": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="DNA sequence (string of A, T, C, G)"
            )
        },
        required=["sequence"]
    ),
    responses={
        200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "gc_content_graph": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Base64-encoded image of the GC content graph"
                )
            }
        ),
        400: "Invalid input"
    }
)
@api_view(["POST"])
def gc_content_graph_view(request):
    sequence = request.data.get("sequence", "")
    if not sequence:
        return Response({"error": "DNA sequence is required."}, status=status.HTTP_400_BAD_REQUEST)
    try:
        graph_image = visualize_gc_content_graph(sequence)
        return Response({"gc_content_graph": graph_image}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Protein Translation View
@swagger_auto_schema(
    method='post',
    operation_summary="Translate DNA to Protein",
    operation_description="Translates a given DNA sequence into its corresponding protein sequence.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "sequence": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="DNA sequence (string of A, T, C, G)"
            )
        },
        required=["sequence"]
    ),
    responses={
        200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "protein_sequence": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="The translated protein sequence"
                )
            }
        ),
        400: "Invalid input"
    }
)
@api_view(["POST"])
def protein_translation_view(request):
    sequence = request.data.get("sequence", "")
    if not sequence:
        return Response({"error": "DNA sequence is required."}, status=status.HTTP_400_BAD_REQUEST)
    try:
        protein_sequence = translate_sequence(sequence)
        return Response({"protein_sequence": protein_sequence}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Mutation Detection View
@swagger_auto_schema(
    method='post',
    operation_summary="Detect DNA Mutations",
    operation_description="Detects mutations between a reference DNA sequence and a user-provided sequence.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "reference_sequence": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="Reference DNA sequence"
            ),
            "user_sequence": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="User-provided DNA sequence"
            )
        },
        required=["reference_sequence", "user_sequence"]
    ),
    responses={
        200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "mutations": openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(type=openapi.TYPE_STRING),
                    description="List of detected mutations"
                )
            }
        ),
        400: "Invalid input"
    }
)
@api_view(["POST"])
def mutation_detection_view(request):
    reference_sequence = request.data.get("reference_sequence", "")
    user_sequence = request.data.get("user_sequence", "")
    if not reference_sequence or not user_sequence:
        return Response({"error": "Both reference and user sequences are required."}, status=status.HTTP_400_BAD_REQUEST)
    try:
        mutations = detect_mutations(reference_sequence, user_sequence)
        return Response({"mutations": mutations}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# DNA Sequence Validation View
@swagger_auto_schema(
    method='post',
    operation_summary="Validate DNA Sequence",
    operation_description="Validates the given DNA sequence for non-ACGT characters.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "sequence": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="DNA sequence (string of A, T, C, G)"
            )
        },
        required=["sequence"]
    ),
    responses={
        200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "message": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Validation message indicating the sequence is valid"
                )
            }
        ),
        400: "Invalid input"
    }
)
@api_view(["POST"])
def sequence_validation_view(request):
    sequence = request.data.get("sequence", "")
    if not sequence:
        return Response({"error": "DNA sequence is required."}, status=status.HTTP_400_BAD_REQUEST)
    try:
        if not validate_sequence(sequence):
            return Response({"error": "Invalid DNA sequence: contains non-ACGT characters."}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message": "DNA sequence is valid."}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Generate PDF Report View
@swagger_auto_schema(
    method='post',
    operation_summary="Generate DNA Analysis Report",
    operation_description="Generates a PDF report summarizing the DNA analysis results.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "sequence": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="DNA sequence (string of A, T, C, G)"
            )
        },
        required=["sequence"]
    ),
    responses={
        200: "PDF report file",
        400: "Invalid input"
    }
)
@api_view(["POST"])
def generate_report_view(request):
    sequence = request.data.get("sequence", "")
    if not sequence:
        return Response({"error": "DNA sequence is required."}, status=status.HTTP_400_BAD_REQUEST)
    try:
        pdf_file = generate_pdf_report(sequence)
        return FileResponse(pdf_file, content_type='application/pdf')
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Interactive GC Content Graph View
@swagger_auto_schema(
    method='post',
    operation_summary="Interactive GC Content Graph",
    operation_description="Generates an interactive GC content graph for the given DNA sequence.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "sequence": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="DNA sequence (string of A, T, C, G)"
            )
        },
        required=["sequence"]
    ),
    responses={
        200: "Interactive graph",
        400: "Invalid input"
    }
)
@api_view(["POST"])
def interactive_gc_content_view(request):
    sequence = request.data.get("sequence", "")
    if not sequence:
        return Response({"error": "DNA sequence is required."}, status=status.HTTP_400_BAD_REQUEST)
    try:
        graph = interactive_gc_content_graph(sequence)
        return Response({"interactive_graph": graph}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@swagger_auto_schema(
    method='post',
    request_body=UserSerializer,
    responses={
        201: "User registered successfully.",
        400: "Invalid input.",
    },
)
@api_view(["POST"])
@permission_classes([AllowAny])
def register_user(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "User registered successfully."}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Login Parameters for Swagger
login_params = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'username': openapi.Schema(type=openapi.TYPE_STRING, description='Username'),
        'password': openapi.Schema(type=openapi.TYPE_STRING, description='Password'),
    },
    required=['username', 'password']
)

# Login User
@swagger_auto_schema(
    method='post',
    request_body=login_params,
    responses={
        200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "refresh": openapi.Schema(type=openapi.TYPE_STRING, description="Refresh token"),
                "access": openapi.Schema(type=openapi.TYPE_STRING, description="Access token"),
            },
        ),
        401: "Invalid credentials.",
        404: "User does not exist.",
    },
)
@api_view(["POST"])
@permission_classes([AllowAny])
def login_user(request):
    username = request.data.get("username")
    password = request.data.get("password")

    try:
        user = User.objects.get(username=username)
        if user.check_password(password):
            refresh = RefreshToken.for_user(user)
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        return Response({"error": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)
    except User.DoesNotExist:
        return Response({"error": "User does not exist."}, status=status.HTTP_404_NOT_FOUND)

# Protected Endpoint Example
@swagger_auto_schema(
    method='get',
    responses={
        200: "Protected endpoint successfully accessed.",
        401: "Unauthorized access.",
    },
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def protected_view(request):
    return Response({"message": "This is a protected endpoint."}, status=status.HTTP_200_OK)