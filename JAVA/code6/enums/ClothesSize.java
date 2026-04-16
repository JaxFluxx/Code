package enums;
import java.util.Scanner;
/**
 * This program demonstrates enumerated types.
 * @version 1.0 2018-10-24
 * @author He Yongqiang
 */
public enum ClothesSize
{
	SMALL("小号",165),MEDIUM("中号",170),LARGE("大号",175),X_LARGE("加大号",180),XX_LARGE("特大号",185);
	private String type;
	private int size;
	
	private ClothesSize(String type,int size)
	{
		this.type=type;
		this.size=size;
	}
	public String getType()
	{
		return type;
	}
	public int getSize()
	{
		return size;
	}
	@Override
	public String toString()
	{
		return type + size;
	}
}

class SizeTest
{
	public static void main(String...strings )
	{
		ClothesSize shirt = ClothesSize.LARGE;
		System.out.println(shirt.name());
		System.out.println(shirt.toString());
		System.out.println(shirt.ordinal());
		
		ClothesSize suit;
		Scanner in =new Scanner(System.in);
		System.out.println("Please input a size to your suit:(SMALL,MEDIUM,LARGE,X_LARGE or XX_LARGE)");
		String input=in.next().toUpperCase();
		suit=Enum.valueOf(ClothesSize.class, input);
		System.out.println("Your choice is:");
		System.out.println(suit.name());
		System.out.println(suit.toString());
		System.out.println(suit.ordinal());
	}
	
}