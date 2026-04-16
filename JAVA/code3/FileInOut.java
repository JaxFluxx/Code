import java.io.IOException;
import java.io.PrintStream;
import java.nio.file.Paths;
import java.util.Scanner;

public class FileInOut
{
	
	public static void main(String[] args) throws IOException
	{
		Scanner in = new Scanner(Paths.get("e:\\temp\\mytest.txt"),"gbk");		
		PrintStream toFile = new PrintStream("e:\\temp\\mytest2.txt","utf-8");
		toFile.println("这是一个新闻报道，讲述了一个事实。");
		while(in.hasNextLine())
			toFile.print(in.nextLine());
	}
}