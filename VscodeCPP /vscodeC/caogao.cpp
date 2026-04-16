#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <math.h>
#include <windows.h>

HANDLE hOut;
HWND myconsole;
HDC hdc;

CONSOLE_SCREEN_BUFFER_INFO cinfo;

typedef struct MyLove {
  double m, n, size;
  int NUMS, x, y;
}MyLove ;

MyLove mylove[400];
int CenterX = 320;
int CenterY = 180;
double Size = 60;

void updata();    
void movedata();  
void showdata();  
void GetRand(int* buf, int count, int range);  

void initdata() 
{
  memset(mylove, 0, sizeof(mylove));
}

void init_game()
{
  hOut = GetStdHandle(STD_OUTPUT_HANDLE);   
  myconsole = GetConsoleWindow();
  hdc = GetDC(myconsole);
  
  SetTextColor(hdc, RGB(255, 0, 0));
  SetTextCharacterExtra(hdc, 1);
  SetBkMode(hdc, TRANSPARENT);
  SetBkColor(hdc, RGB(0, 0, 0));
}

void clear_screen()
{
  DWORD c;
  GetConsoleScreenBufferInfo(hOut,&cinfo); 
  COORD pos = {0, 0};
  FillConsoleOutputCharacter(hOut, 0x20, cinfo.dwSize.X*cinfo.dwSize.Y, pos, &c);
    
  CONSOLE_CURSOR_INFO coord = {1, 0};
  SetConsoleCursorInfo(hOut, &coord);  
}

int main() {
  init_game();
  initdata();
  updata();
  while (1) {
    clear_screen() ;
    updata();
    showdata();
    Sleep(50);
  }
  return 0;
}

void updata() {
  int* buf = (int*)malloc(sizeof(int)* 20);
  GetRand(buf, 20, (int)(2 * Size / 0.01));
  movedata();
  
  for (int i = 0; i < 20; i++) {
    mylove[i].m = buf[i] * 0.01;
    mylove[i].n = (((sin(buf[(int)i] * 0.01) * sqrt(fabs(cos(buf[(int)i] * 0.01)))) / (sin(buf[(int)i] * 0.01) + 1.4142)) - 2 * sin(buf[(int)i] * 0.01) + 2);
    mylove[i].size = Size;
    mylove[i].NUMS = i / 20;
    mylove[i].x = (int)(-Size *mylove[i].n * cos(mylove[i].m) + CenterX);
    mylove[i].y = (int)(-Size *mylove[i].n * sin(mylove[i].m) + CenterY - mylove[i].size);
  }
  
  for (int i = 20; i < 400; i++) {
    mylove[i].size = mylove[i].size + 1;
    if (mylove[i].size>80) {
      mylove[i].size = 80;
    }
    mylove[i].NUMS = i / 20;
    mylove[i].x = (int)(-mylove[i].size *mylove[i].n * cos(mylove[i].m) + CenterX);
    mylove[i].y = (int)(-mylove[i].size *mylove[i].n * sin(mylove[i].m) + CenterY - mylove[i].size);
  }
  
  free(buf);
}

void movedata() {
  for (int i = 399; i > 19; i--) {
    mylove[i] = mylove[i - 20];
  }
}

void showdata() 
{
  for (int i = 0; i < 400; i++) {
	TextOut(hdc, mylove[i].x + 20, mylove[i].y + 20, "*", 1); 
  }
}

void GetRand(int* buf, int count, int range) 
{
  struct timeb timeSeed;
  ftime(&timeSeed);
  srand(timeSeed.time * 1000 + timeSeed.millitm);  // milli time
  
  for (int i = 0; i < count; i++) {
    int randTmp = rand() % range;
    for (int j = 0; j < i; j++) {
      if (buf[j] == randTmp) {
        break; 
      }
    }
    buf[i] = randTmp;
  }
}